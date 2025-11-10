import pytest
from urllib.parse import urlparse, parse_qs

# Import the implementation module and use its internal URL-construction seam
from image_downloader import ImageDownloader


def construct_search_url(filters: dict) -> str:
    """Build a Google Images search URL without hitting the network.

    Uses the internal, exposed URL-construction seam in ImageDownloader:
    - _build_url_parameters(filters) -> "&tbs=..." (or "")
    - _build_search_url(query, params, filters) -> full search URL
    """
    downloader = ImageDownloader()
    params = downloader._build_url_parameters(filters or {})
    return downloader._build_search_url("test", params, filters or {})


def extract_tbs(url: str) -> str:
    """Extract the tbs parameter value from a URL, order-agnostic."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    # parse_qs returns a list for each key
    tbs_values = query.get("tbs", [])
    return tbs_values[0] if tbs_values else ""


def test_exact_size_valid_appends_expected_fragments():
    filters = {"exact_size": "800,600"}
    url = construct_search_url(filters)
    tbs = extract_tbs(url)

    # Expect exact size fragments
    assert "isz:ex" in tbs
    assert "iszw:800" in tbs
    assert "iszh:600" in tbs

    # Ensure no duplicates
    assert tbs.count("isz:ex") == 1
    assert tbs.count("iszw:800") == 1
    assert tbs.count("iszh:600") == 1


def test_time_range_valid_appends_expected_fragments():
    filters = {"time_range": {"time_min": "01/01/2020", "time_max": "12/31/2020"}}
    url = construct_search_url(filters)
    tbs = extract_tbs(url)

    # Expect time range fragments
    assert "cdr:1" in tbs
    assert "cd_min:01/01/2020" in tbs
    assert "cd_max:12/31/2020" in tbs

    # Ensure no duplicates
    assert tbs.count("cdr:1") == 1
    assert tbs.count("cd_min:01/01/2020") == 1
    assert tbs.count("cd_max:12/31/2020") == 1


def test_combined_exact_size_and_time_range_compose_without_duplicates():
    filters = {
        "exact_size": "800,600",
        "time_range": {"time_min": "01/01/2020", "time_max": "12/31/2020"},
    }
    url = construct_search_url(filters)
    tbs = extract_tbs(url)

    # All expected fragments should be present exactly once
    expectations = [
        "isz:ex",
        "iszw:800",
        "iszh:600",
        "cdr:1",
        "cd_min:01/01/2020",
        "cd_max:12/31/2020",
    ]

    for fragment in expectations:
        assert fragment in tbs
        assert tbs.count(fragment) == 1


@pytest.mark.parametrize(
    "bad_exact_size",
    [
        "foo",       # not a pair
        "800x600",   # wrong separator
        "800,",      # missing height
        ",600",      # missing width
        "800,abc",   # non-numeric
        "x,y",       # non-numeric pair
    ],
)
def test_exact_size_invalid_inputs_do_not_append_fragments(bad_exact_size):
    filters = {"exact_size": bad_exact_size}
    url = construct_search_url(filters)
    tbs = extract_tbs(url)

    # None of the exact-size fragments should appear
    assert "isz:ex" not in tbs
    assert "iszw:" not in tbs
    assert "iszh:" not in tbs


@pytest.mark.parametrize(
    "bad_time_range",
    [
        {},  # empty dict
        {"time_min": "01/01/2020"},  # only min
        {"time_max": "12/31/2020"},  # only max
        {"time_min": "2020-01-01", "time_max": "2020-12-31"},  # wrong format
        {"time_min": "01/01/2020", "time_max": ""},  # empty max
        {"time_min": "", "time_max": "12/31/2020"},  # empty min
    ],
)
def test_time_range_invalid_inputs_do_not_append_fragments(bad_time_range):
    filters = {"time_range": bad_time_range}
    url = construct_search_url(filters)
    tbs = extract_tbs(url)

    # None of the time-range fragments should appear
    assert "cdr:1" not in tbs
    assert "cd_min:" not in tbs
    assert "cd_max:" not in tbs
