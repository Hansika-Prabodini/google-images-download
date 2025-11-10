import pytest
from image_downloader import ImageDownloader


def test_build_url_parameters_teal_color():
    downloader = ImageDownloader()
    params = downloader._build_url_parameters({'color': 'teal'})
    # Before patch, this contained 'isc:teel' (typo). After patch it should be correct.
    assert 'ic:specific,isc:teal' in params
    assert 'isc:teel' not in params
