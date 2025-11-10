import pytest
from urllib.parse import urlparse, parse_qs

# Use the public URL-construction helper exposed for tests
from image_downloader import build_search_url_for_test


def test_color_teal_and_raw_format_tbs_fragments_present():
    # Build URL deterministically without any network calls
    filters = {
        'color': 'teal',
        'format': 'raw',
    }
    url = build_search_url_for_test('test query', filters)

    # Parse query string to extract tbs parameter
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    tbs_values = query_params.get('tbs')

    assert tbs_values, "Expected 'tbs' parameter to be present in the URL"
    tbs = tbs_values[0]

    # Assert mappings without depending on ordering of fragments
    assert 'ic:specific,isc:teal' in tbs, "Expected corrected teal color mapping in tbs"
    assert 'ift:craw' in tbs, "Expected raw format to map to ift:craw in tbs"

    # Guard against regression of the misspelled teal mapping
    assert 'isc:teel' not in tbs, "Did not expect misspelled 'isc:teel' in tbs"
