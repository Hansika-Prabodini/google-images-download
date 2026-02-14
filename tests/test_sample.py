# Sample tests for google_images_download functionality
import pytest
from google_images_download import google_images_download


def test_class_instantiation():
    """Test that the googleimagesdownload class can be instantiated properly."""
    gid = google_images_download.googleimagesdownload()
    assert gid is not None
    assert hasattr(gid, 'download')
    assert callable(getattr(gid, 'download'))


def test_argument_validation():
    """Test that proper argument validation occurs for required parameters."""
    gid = google_images_download.googleimagesdownload()
    
    # Test that missing keywords raises appropriate behavior
    empty_args = {
        'keywords': None,
        'keywords_from_file': None,
        'single_image': None,
        'url': None,
        'similar_images': None
    }
    
    # The download method should handle missing keywords gracefully
    # by either returning an error or exiting (which we can't test directly)
    # So we test that it doesn't crash unexpectedly
    try:
        paths, errors = gid.download(empty_args)
        # If it returns, we expect an error count or empty paths
        assert isinstance(paths, dict)
        assert isinstance(errors, int) or errors is None
    except SystemExit:
        # This is expected behavior for missing keywords
        pass


def test_basic_functionality():
    """Test basic functionality with minimal valid arguments."""
    gid = google_images_download.googleimagesdownload()
    
    # Test with minimal valid arguments that shouldn't actually download
    test_args = {
        'keywords': 'test',
        'limit': 1,
        'no_download': True,  # Prevent actual downloading
        'silent_mode': True   # Suppress output
    }
    
    # This should execute without crashing
    paths, errors = gid.download(test_args)
    assert isinstance(paths, dict)
    assert isinstance(errors, int) or errors is None
