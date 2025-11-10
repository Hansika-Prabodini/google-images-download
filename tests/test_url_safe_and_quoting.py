# -*- coding: utf-8 -*-
"""
Tests for Google Images URL construction: safe_search behavior and term quoting.

These tests are hermetic and rely only on the URL-building helper exposed for tests.
If the helper is not yet available (future task dependency), they fall back to
using the internal builder from image_downloader to keep tests deterministic.
"""

from urllib.parse import urlparse, parse_qs

# Attempt to import the public test helper; provide a fallback if missing.
try:
    from image_downloader import build_search_url_for_test  # type: ignore
except Exception:  # pragma: no cover - fallback for current repo state
    # Fallback: build using the internal helper methods. This keeps the tests
    # hermetic and allows them to run before the public helper is introduced.
    import image_downloader as _img

    def build_search_url_for_test(search_term, filters=None):  # noqa: N802 (match expected name)
        downloader = _img.ImageDownloader()
        params = downloader._build_url_parameters(filters or {})  # pylint: disable=protected-access
        return downloader._build_search_url(search_term, params, filters or {})  # pylint: disable=protected-access


def test_safe_search_true_adds_safe_active():
    url = build_search_url_for_test("kittens", filters={"safe_search": True})
    parsed = urlparse(url)
    q = parse_qs(parsed.query)

    assert "safe" in q, "Expected 'safe' parameter to be present when safe_search=True"
    assert q["safe"] == ["active"], "Expected safe=active when safe_search=True"


def test_safe_search_false_omits_safe():
    # Explicit False should omit the parameter
    url = build_search_url_for_test("puppies", filters={"safe_search": False})
    parsed = urlparse(url)
    q = parse_qs(parsed.query)

    assert "safe" not in q, "Expected no 'safe' parameter when safe_search=False"


def test_term_quoting_uses_quote_plus():
    term = "café au lait"
    url = build_search_url_for_test(term)

    # We validate quoting by checking the raw URL contains q=caf%C3%A9+au+lait
    # which implies quote_plus semantics: spaces become '+', non-ASCII percent-encoded.
    assert "q=caf%C3%A9+au+lait" in url, (
        "Expected search term to be encoded with quote_plus semantics: "
        "'café au lait' -> 'caf%C3%A9+au+lait'"
    )

    # Also assert '+' is used for spaces and '%C3%A9' percent-encodes 'é'
    assert "+au+" in url, "Expected '+' characters in place of spaces in the query string"
    assert "%C3%A9" in url, "Expected UTF-8 percent-encoding for 'é' in the query string"
