import importlib
from urllib.parse import urlparse, parse_qs

# Try to import the public helper. If absent, fall back to building via ImageDownloader internals.
try:
    from image_downloader import build_search_url_for_test  # type: ignore
except Exception:
    build_search_url_for_test = None  # type: ignore


def _fallback_build_search_url_for_test(query: str, filters: dict) -> str:
    """Deterministically build the search URL without any network using ImageDownloader internals.
    This mirrors the public helper expected to exist in later tasks, while keeping tests stable now.
    """
    from image_downloader import ImageDownloader  # local import to avoid import cycles during collection

    dl = ImageDownloader()
    params = dl._build_url_parameters(filters or {})  # noqa: SLF001 - used intentionally for deterministic build
    return dl._build_search_url(query, params, filters or {})  # noqa: SLF001


def build_url(query: str, filters: dict) -> str:
    if build_search_url_for_test is not None:
        return build_search_url_for_test(query, filters)
    return _fallback_build_search_url_for_test(query, filters)


def get_tbs(filters: dict) -> str:
    url = build_url("test", filters)
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    # parse_qs returns list values; join first value if present
    tbs_values = qs.get("tbs", [])
    if not tbs_values:
        return ""
    return tbs_values[0]


def assert_fragments_in_tbs(tbs: str, fragments: list[str]):
    for frag in fragments:
        assert frag in tbs, f"Expected fragment '{frag}' in tbs='{tbs}'"


def test_size_large_maps_isz_l():
    tbs = get_tbs({"size": "large"})
    assert_fragments_in_tbs(tbs, ["isz:l"])


def test_type_clipart_maps_itp_clipart():
    tbs = get_tbs({"type": "clipart"})
    assert_fragments_in_tbs(tbs, ["itp:clipart"])


def test_time_past_24_hours_maps_qdr_d():
    tbs = get_tbs({"time": "past-24-hours"})
    assert_fragments_in_tbs(tbs, ["qdr:d"])


def test_format_jpg_maps_ift_jpg():
    tbs = get_tbs({"format": "jpg"})
    assert_fragments_in_tbs(tbs, ["ift:jpg"])


def test_combined_filters_compose():
    filters = {
        "size": "large",
        "type": "clipart",
        "time": "past-24-hours",
        "format": "jpg",
    }
    tbs = get_tbs(filters)
    expected = ["isz:l", "itp:clipart", "qdr:d", "ift:jpg"]
    assert_fragments_in_tbs(tbs, expected)
