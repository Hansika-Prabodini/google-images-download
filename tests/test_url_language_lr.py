import pytest
from urllib.parse import urlparse, parse_qs

# Prefer the public helper exposed for tests; fall back to private internals if not available
try:
    from image_downloader import build_search_url_for_test  # type: ignore
except Exception:
    build_search_url_for_test = None

# Fallback builder uses ImageDownloader internals to deterministically build URLs without network
if build_search_url_for_test is None:
    from image_downloader import ImageDownloader  # type: ignore

    def build_search_url_for_test(query: str, filters: dict | None = None) -> str:
        downloader = ImageDownloader()
        params = downloader._build_url_parameters(filters or {})
        return downloader._build_search_url(query, params, filters)


def parse_query(url: str) -> dict:
    parsed = urlparse(url)
    return parse_qs(parsed.query)


def test_language_name_maps_to_lr_code():
    url = build_search_url_for_test("flowers", {"language": "English"})
    qs = parse_query(url)
    assert "lr" in qs, f"Expected 'lr' parameter in URL query. URL: {url}"
    assert qs["lr"] == ["lang_en"], f"Expected lr=['lang_en'], got {qs['lr']} from URL: {url}"


def test_language_code_pass_through():
    url = build_search_url_for_test("flowers", {"language": "lang_fr"})
    qs = parse_query(url)
    assert "lr" in qs, f"Expected 'lr' parameter in URL query. URL: {url}"
    assert qs["lr"] == ["lang_fr"], f"Expected lr=['lang_fr'], got {qs['lr']} from URL: {url}"


def test_language_unknown_omits_lr():
    url = build_search_url_for_test("flowers", {"language": "UnknownLanguage"})
    qs = parse_query(url)
    assert "lr" not in qs, f"Did not expect 'lr' parameter in URL query for unknown language. URL: {url}"
