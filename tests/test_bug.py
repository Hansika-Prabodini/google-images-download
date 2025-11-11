import re
from image_downloader import ImageDownloader


def test_build_url_parameters_teal_color_mapping():
    downloader = ImageDownloader()
    params = downloader._build_url_parameters({'color': 'teal'})
    # Ensure parameters string starts with &tbs=
    assert params.startswith('&tbs='), 'URL parameters should start with &tbs='

    # Extract the tbs value after &tbs=
    tbs_value = params[len('&tbs='):]

    # The color mapping should include 'isc:teal' not the misspelled 'isc:teel'
    assert 'isc:teal' in tbs_value, 'Teal color should map to isc:teal'
    assert 'isc:teel' not in tbs_value, 'Teal color must not map to isc:teel'
