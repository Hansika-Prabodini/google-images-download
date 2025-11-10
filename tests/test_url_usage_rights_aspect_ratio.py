import urllib.parse as urlparse
from urllib.parse import parse_qs

import pytest

import image_downloader


def build_search_url(query: str, filters: dict | None = None) -> str:
    """
    Build a deterministic Google Images search URL using the exposed
    URL-construction seam. If the public seam is not available, fall back to
    the ImageDownloader private helpers (no network requests).
    """
    filters = filters or {}

    # Prefer a public seam if one was exposed for tests in earlier tasks
    public_names = (
        "build_search_url_for_tests",
        "construct_search_url",
        "build_test_search_url",
    )
    for name in public_names:
        fn = getattr(image_downloader, name, None)
        if callable(fn):
            return fn(query, filters)

    # Fallback: use the class internals to build the URL (pure string ops)
    downloader = image_downloader.ImageDownloader()
    params = downloader._build_url_parameters(filters)
    return downloader._build_search_url(query, params, filters)


def extract_tbs(url: str) -> str:
    """Extract the 'tbs' query parameter from a Google Images URL."""
    parsed = urlparse.urlparse(url)
    qs = parse_qs(parsed.query)
    tbs_values = qs.get("tbs", [])
    return tbs_values[0] if tbs_values else ""


@pytest.mark.parametrize(
    "usage_rights,expected_fragment",
    [
        ("labeled-for-reuse-with-modifications", "sur:fmc"),
        ("labeled-for-reuse", "sur:fc"),
        ("labeled-for-noncommercial-reuse-with-modification", "sur:fm"),
        ("labeled-for-nocommercial-reuse", "sur:f"),
    ],
)
def test_usage_rights_maps_to_sur_fragment(usage_rights, expected_fragment):
    url = build_search_url("test", filters={"usage_rights": usage_rights})
    tbs = extract_tbs(url)
    assert expected_fragment in tbs


@pytest.mark.parametrize(
    "aspect_ratio,expected_fragment",
    [
        ("tall", "iar:t"),
        ("square", "iar:s"),
        ("wide", "iar:w"),
        ("panoramic", "iar:xw"),
    ],
)
def test_aspect_ratio_maps_to_iar_fragment(aspect_ratio, expected_fragment):
    url = build_search_url("test", filters={"aspect_ratio": aspect_ratio})
    tbs = extract_tbs(url)
    assert expected_fragment in tbs


def test_combined_usage_rights_and_aspect_ratio_composes_single_tbs_without_duplicates():
    filters = {
        "usage_rights": "labeled-for-reuse",
        "aspect_ratio": "square",
    }
    url = build_search_url("test", filters=filters)
    tbs = extract_tbs(url)

    # Both fragments must be present
    assert "sur:fc" in tbs
    assert "iar:s" in tbs

    # No duplicates of either fragment
    assert tbs.count("sur:fc") == 1
    assert tbs.count("iar:s") == 1


def test_invalid_usage_rights_does_not_add_sur_fragment():
    url = build_search_url("test", filters={"usage_rights": "invalid"})
    tbs = extract_tbs(url)
    assert "sur:" not in tbs


def test_invalid_aspect_ratio_does_not_add_iar_fragment():
    url = build_search_url("test", filters={"aspect_ratio": "invalid"})
    tbs = extract_tbs(url)
    assert "iar:" not in tbs


def test_invalid_both_does_not_add_sur_or_iar_fragments():
    url = build_search_url("test", filters={"usage_rights": "invalid", "aspect_ratio": "invalid"})
    tbs = extract_tbs(url)
    assert "sur:" not in tbs
    assert "iar:" not in tbs
