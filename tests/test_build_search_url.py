import re
from image_downloader import ImageDownloader


def test_build_search_url_ascii_query():
    downloader = ImageDownloader()
    url = downloader._build_search_url('dogs', '', None)
    assert isinstance(url, str)
    # Ensure query parameter is present and correctly encoded
    assert re.search(r"[?&]q=dogs(?!\S)", url)


def test_build_search_url_unicode_query():
    downloader = ImageDownloader()
    url = downloader._build_search_url('café', '', None)
    assert isinstance(url, str)
    # UTF-8 percent-encoding for 'café' is caf%C3%A9
    assert 'q=caf%25C3%25A9' not in url  # ensure not double-encoded
    assert 'q=caf%C3%A9' in url


def test_build_search_url_with_safe_search():
    downloader = ImageDownloader()
    url = downloader._build_search_url('kittens', '', {'safe_search': True})
    assert '&safe=active' in url
