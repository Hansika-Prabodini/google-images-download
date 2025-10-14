"""Sample Test passing with nose and pytest.

This module contains a simple test to verify the test framework is working correctly.
"""


def test_pass():
    """A simple test that verifies basic assertions work.
    
    This test ensures the test framework (nose/pytest) is properly configured
    and can execute tests successfully.
    """
    assert True, "dummy sample test"


def test_module_import():
    """Test that the main module can be imported without errors.
    
    This verifies the basic package structure is intact and importable.
    """
    try:
        import google_images_download
        assert google_images_download is not None
    except ImportError as e:
        assert False, f"Failed to import google_images_download: {e}"
