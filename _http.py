"""
Internal HTTP client with thread-safe User-Agent rotation.

This module defines _HttpClient which provides a minimal abstraction over
urllib.request for making HTTP requests while injecting a rotating
User-Agent header. It supports:
- Default shipped UA pool
- Custom UA pool via constructor
- Custom UA pool via IMGDL_UA_FILE environment variable
- Per-call override via explicit user_agent parameter or headers

Note: This is an internal helper; not part of the public API surface.
"""

from __future__ import annotations

import os
import threading
from typing import Dict, Iterable, List, Optional, Tuple

# Python 3 only codebase per project structure
import urllib.request
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl


_DEFAULT_USER_AGENTS: Tuple[str, ...] = (
    # Desktop Chrome (Windows)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # Desktop Chrome (macOS)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # Desktop Chrome (Linux)
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # Desktop Firefox (Windows)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Desktop Edge (Windows Chromium)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/121.0.0.0 Chrome/121.0.0.0 Safari/537.36",
    # Mobile Safari (iPhone iOS 17)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    # Mobile Safari (iPad iPadOS 17)
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    # Mobile Chrome (Android 14 Pixel 7)
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.216 Mobile Safari/537.36",
)


class _HttpClient:
    """Minimal HTTP client with thread-safe User-Agent rotation.

    The client wraps urllib.request to inject a rotating User-Agent header.
    It is intentionally small to avoid altering public APIs of the library.
    """

    def __init__(self, user_agents: Optional[List[str]] = None):
        # Load UA pool from constructor, env file, or defaults.
        loaded_pool = self._load_user_agents_from_env()
        if user_agents and isinstance(user_agents, (list, tuple)):
            # Use constructor-provided list if non-empty after cleaning
            cleaned = [ua.strip() for ua in user_agents if isinstance(ua, str) and ua.strip()]
            if cleaned:
                loaded_pool = tuple(cleaned)
        if not loaded_pool:
            loaded_pool = _DEFAULT_USER_AGENTS
        self._user_agents: Tuple[str, ...] = loaded_pool

        # Thread-safe round-robin state
        self._ua_lock = threading.Lock()
        self._ua_index = 0

        # Prepare a default SSL context mirroring existing code's behavior
        self._ssl_context = ssl.create_default_context()

    def _load_user_agents_from_env(self) -> Tuple[str, ...]:
        """Load UAs from IMGDL_UA_FILE if present.

        The file should be newline-delimited; lines starting with '#' or blank
        lines are ignored. Returns tuple of UAs or empty tuple if unavailable.
        """
        path = os.getenv("IMGDL_UA_FILE")
        if not path:
            return tuple()
        try:
            agents: List[str] = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    agents.append(line)
            return tuple(agents)
        except Exception:
            # Silently fall back to defaults per spec
            return tuple()

    def _next_user_agent(self) -> str:
        """Return the next UA in round-robin order with thread safety."""
        with self._ua_lock:
            if not self._user_agents:
                return ""
            ua = self._user_agents[self._ua_index]
            self._ua_index = (self._ua_index + 1) % len(self._user_agents)
            return ua

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        *,
        user_agent: Optional[str] = None,
        timeout: Optional[float] = None,
        data: Optional[bytes] = None,
    ):
        """Make an HTTP request with optional UA rotation.

        Args:
            method: HTTP method (GET, POST, ...)
            url: URL to request
            headers: Optional headers dict. If it includes a User-Agent, it is
                respected and no rotation occurs.
            user_agent: Explicit UA to use for this call; overrides rotation
                and header injection policy.
            timeout: Optional timeout in seconds
            data: Optional request body bytes

        Returns:
            The HTTPResponse-like object from urllib.request.urlopen
        """
        # Start from headers or an empty mapping
        hdrs: Dict[str, str] = dict(headers) if headers else {}

        # Case-insensitive detection for existing UA header
        has_ua = any(k.lower() == "user-agent" for k in hdrs.keys())

        # Apply explicit per-call override if provided
        if user_agent is not None:
            hdrs["User-Agent"] = user_agent
        elif not has_ua:
            hdrs["User-Agent"] = self._next_user_agent()

        # Build and perform the request
        req = Request(url=url, data=data, headers=hdrs, method=method.upper())
        return urlopen(req, context=self._ssl_context, timeout=timeout)


__all__ = ["_HttpClient"]
