import pytest
from google_images_download.google_images_download import googleimagesdownload


def test_build_url_parameters_size_mapping():
    gid = googleimagesdownload()
    # Build parameters with size '>1024*768'
    arguments = {k: None for k in [
        "keywords", "keywords_from_file", "prefix_keywords", "suffix_keywords",
        "limit", "format", "color", "color_type", "usage_rights", "size",
        "exact_size", "aspect_ratio", "type", "time", "time_range", "delay", "url", "single_image",
        "output_directory", "image_directory", "no_directory", "proxy", "similar_images", "specific_site",
        "print_urls", "print_size", "print_paths", "metadata", "extract_metadata", "socket_timeout",
        "thumbnail", "thumbnail_only", "language", "prefix", "chromedriver", "related_images", "safe_search", "no_numbering",
        "offset", "no_download","save_source","silent_mode","ignore_urls"
    ]}
    arguments['size'] = '>1024*768'
    params = gid.build_url_parameters(arguments)

    # Before patch, there was a typo 'visz' instead of 'isz'. Ensure it's corrected.
    assert 'isz:lt,islt:xga' in params
    assert 'visz:lt,islt:xga' not in params
