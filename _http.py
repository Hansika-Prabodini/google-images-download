"""
Internal HTTP client with manual retry logic, exponential backoff, and jitter.

This module provides a centralized _HttpClient that wraps requests.Session
and implements application-level retries with configuration and per-call
overrides.
"""
from __future__ import annotations

import logging
import time
import random
import http.client
from typing import Any, Dict, Optional, Tuple, Callable

import requests
from requests import Response

try:
    # urllib3 is a transitive dependency of requests
    from urllib3.exceptions import ProtocolError  # type: ignore
except Exception:  # pragma: no cover - fallback if urllib3 API changes
    ProtocolError = tuple()  # type: ignore

# Public API remains the same (module-private client)


class _HttpClient:
    """A thin wrapper around requests.Session with manual retry support.

    Configuration is provided at construction time, with per-call overrides
    available on request().
    """

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        *,
        # Retry config defaults
        max_retries: int = 3,
        backoff_base: float = 0.5,
        backoff_jitter: float = 0.2,
        max_backoff_total: float = 15.0,
        # Deterministic jitter seed for tests
        jitter_seed: Optional[int] = None,
        # Dependency injection for unit tests
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self._session = session or requests.Session()
        self._max_retries = int(max_retries)
        self._backoff_base = float(backoff_base)
        self._backoff_jitter = float(backoff_jitter)
        self._max_backoff_total = float(max_backoff_total)
        self._sleep = sleep_fn

        # Private RNG for jitter to enable deterministic tests
        self._rand = random.Random(jitter_seed)

        # Logger
        self._log = logging.getLogger(__name__)

    # region Internal helpers
    _RETRYABLE_STATUS = {429}  # union with 5xx handled dynamically

    @staticmethod
    def _is_retryable_exception(exc: BaseException) -> bool:
        retryable = (
            isinstance(exc, requests.Timeout)
            or isinstance(exc, requests.ConnectionError)
            or isinstance(exc, ProtocolError)
            or isinstance(exc, http.client.IncompleteRead)
            or (
                hasattr(http.client, "BadStatusLine")
                and isinstance(exc, http.client.BadStatusLine)  # type: ignore[attr-defined]
            )
        )
        return bool(retryable)

    @staticmethod
    def _is_retryable_status(status: int) -> bool:
        if status == 429:
            return True
        if 500 <= status <= 599:
            return True
        return False

    def _compute_backoff(self, attempt_index: int, *, base: float, jitter: float) -> float:
        # attempt_index is 1-based for retries
        expo = base * (2 ** (attempt_index - 1))
        jitter_part = self._rand.uniform(0.0, max(0.0, jitter)) if jitter > 0 else 0.0
        return expo + jitter_part

    # endregion

    def request(
        self,
        method: str,
        url: str,
        *,
        # forwarded to requests.Session.request
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        files: Optional[Any] = None,
        auth: Optional[Any] = None,
        timeout: Optional[Any] = None,
        allow_redirects: bool = True,
        proxies: Optional[Dict[str, str]] = None,
        hooks: Optional[Any] = None,
        stream: bool = False,
        verify: Optional[Any] = None,
        cert: Optional[Any] = None,
        # per-call retry overrides
        max_retries: Optional[int] = None,
        backoff_base: Optional[float] = None,
        backoff_jitter: Optional[float] = None,
        max_backoff_total: Optional[float] = None,
    ) -> Response:
        """Make an HTTP request with manual retries.

        On final failure with a response, raise_for_status() is invoked
        before returning to provide HTTPError to callers for non-2xx status.
        """
        # Resolve effective retry config for this call
        eff_max_retries = self._max_retries if max_retries is None else int(max_retries)
        eff_backoff_base = self._backoff_base if backoff_base is None else float(backoff_base)
        eff_backoff_jitter = self._backoff_jitter if backoff_jitter is None else float(backoff_jitter)
        eff_max_backoff_total = self._max_backoff_total if max_backoff_total is None else float(max_backoff_total)

        attempts = 0
        cumulative_sleep = 0.0
        last_exception: Optional[BaseException] = None
        last_response: Optional[Response] = None

        while True:
            try:
                # Important: do not enable adapter-level retries; we handle them here.
                last_response = self._session.request(
                    method,
                    url,
                    params=params,
                    data=data,
                    json=json,
                    headers=headers,
                    cookies=cookies,
                    files=files,
                    auth=auth,
                    timeout=timeout,
                    allow_redirects=allow_redirects,
                    proxies=proxies,
                    hooks=hooks,
                    stream=stream,
                    verify=verify,
                    cert=cert,
                )

                status = last_response.status_code
                if not self._is_retryable_status(status):
                    # Non-retryable (including success or non-429 4xx). Return/raise below
                    break

                # Retryable status (429/5xx)
                if attempts >= eff_max_retries:
                    break  # out of retries; handle below

                # Respect Retry-After on 429 if integer seconds
                sleep_seconds = None
                if status == 429:
                    ra = last_response.headers.get("Retry-After")
                    if ra is not None:
                        try:
                            val = int(ra.strip())
                            if val >= 0:
                                sleep_seconds = float(val)
                        except (ValueError, TypeError):
                            # Ignore invalid header formats and fall back to backoff
                            pass

                if sleep_seconds is None:
                    sleep_seconds = self._compute_backoff(attempts + 1, base=eff_backoff_base, jitter=eff_backoff_jitter)

                capped = False
                if cumulative_sleep + sleep_seconds > eff_max_backoff_total:
                    # Cap and stop retrying further after this (or skip sleep at all)
                    remaining = max(0.0, eff_max_backoff_total - cumulative_sleep)
                    if remaining <= 0.0:
                        self._log.debug(
                            "Retry cap reached; attempts=%s, reason=status_%s, cumulative_sleep=%.3f >= max_total=%.3f",
                            attempts,
                            status,
                            cumulative_sleep,
                            eff_max_backoff_total,
                        )
                        break
                    sleep_seconds = remaining
                    capped = True

                self._log.debug(
                    "Retrying HTTP %s %s due to status %s (attempt %s/%s). Sleeping %.3fs%s",
                    method,
                    url,
                    status,
                    attempts + 1,
                    eff_max_retries,
                    sleep_seconds,
                    " [capped]" if capped else "",
                )

                # Close the response before retry to avoid leaking connections
                try:
                    last_response.close()
                except Exception:
                    pass

                self._sleep(sleep_seconds)
                cumulative_sleep += sleep_seconds
                attempts += 1
                continue

            except BaseException as exc:
                last_exception = exc
                if not self._is_retryable_exception(exc) or attempts >= eff_max_retries:
                    break

                sleep_seconds = self._compute_backoff(attempts + 1, base=eff_backoff_base, jitter=eff_backoff_jitter)
                capped = False
                if cumulative_sleep + sleep_seconds > eff_max_backoff_total:
                    remaining = max(0.0, eff_max_backoff_total - cumulative_sleep)
                    if remaining <= 0.0:
                        self._log.debug(
                            "Retry cap reached; attempts=%s, reason=%s, cumulative_sleep=%.3f >= max_total=%.3f",
                            attempts,
                            exc.__class__.__name__,
                            cumulative_sleep,
                            eff_max_backoff_total,
                        )
                        break
                    sleep_seconds = remaining
                    capped = True

                self._log.debug(
                    "Retrying HTTP %s %s due to %s (attempt %s/%s). Sleeping %.3fs%s",
                    method,
                    url,
                    exc.__class__.__name__,
                    attempts + 1,
                    eff_max_retries,
                    sleep_seconds,
                    " [capped]" if capped else "",
                )
                self._sleep(sleep_seconds)
                cumulative_sleep += sleep_seconds
                attempts += 1
                continue

        # Final outcome handling
        if last_exception is not None:
            # Final failure was an exception; re-raise
            raise last_exception

        assert last_response is not None  # for type checkers
        # For non-2xx, requests normally raises HTTPError when raise_for_status() is called
        try:
            last_response.raise_for_status()
        except requests.HTTPError:
            # For deterministic behavior, raise after closing the response when not streaming
            if not stream:
                try:
                    last_response.close()
                except Exception:
                    pass
            raise
        return last_response
