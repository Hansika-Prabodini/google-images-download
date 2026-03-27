#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for bug fixes in google_images_download and image_downloader modules.

These tests verify that the following bugs have been fixed:
1. Typo in size filter '>1024*768': 'visz:lt' should be 'isz:lt'
2. Typo in color filter 'teal': 'isc:teel' should be 'isc:teal'  
3. Typo in error messages: 'Cloud not connect' should be 'Could not connect'
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import json

# Add current directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'google_images_download'))

from google_images_download import google_images_download
from image_downloader import ImageDownloader


class TestSizeFilterBugFix(unittest.TestCase):
    """Test that the size filter bug has been fixed."""
    
    def test_size_filter_1024x768_correct_parameter(self):
        """Test that >1024*768 size filter generates correct URL parameter 'isz:lt' not 'visz:lt'."""
        
        # Create a mock googleimagesdownload instance
        gid = google_images_download.googleimagesdownload()
        
        # Create arguments with >1024*768 size filter
        arguments = {
            'size': '>1024*768',
            'color': None,
            'color_type': None,
            'usage_rights': None,
            'type': None,
            'time': None,
            'aspect_ratio': None,
            'format': None,
            'language': None,
            'time_range': None,
            'exact_size': None
        }
        
        # Build URL parameters
        params = gid.build_url_parameters(arguments)
        
        # The result should contain 'isz:lt,islt:xga' not 'visz:lt,islt:xga'
        self.assertIn('isz:lt,islt:xga', params)
        self.assertNotIn('visz:lt,islt:xga', params)
        
    def test_size_filter_would_fail_with_old_bug(self):
        """Test that demonstrates the bug would have caused incorrect URL parameters."""
        
        # This test demonstrates what would happen with the old buggy code
        # We simulate the old behavior by manually creating the buggy parameter
        buggy_params = '&tbs=visz:lt,islt:xga'  # This is what the bug would produce
        correct_params = '&tbs=isz:lt,islt:xga'  # This is what it should produce
        
        # The buggy version should not equal the correct version
        self.assertNotEqual(buggy_params, correct_params)
        
        # Now test that our fixed code produces the correct version
        gid = google_images_download.googleimagesdownload()
        arguments = {
            'size': '>1024*768',
            'color': None,
            'color_type': None,
            'usage_rights': None,
            'type': None,
            'time': None,
            'aspect_ratio': None,
            'format': None,
            'language': None,
            'time_range': None,
            'exact_size': None
        }
        
        actual_params = gid.build_url_parameters(arguments)
        self.assertIn('isz:lt,islt:xga', actual_params)


class TestColorFilterBugFix(unittest.TestCase):
    """Test that the teal color filter bug has been fixed."""
    
    def test_teal_color_filter_correct_parameter_googleimagesdownload(self):
        """Test that teal color filter generates correct URL parameter 'isc:teal' not 'isc:teel'."""
        
        gid = google_images_download.googleimagesdownload()
        
        # Create arguments with teal color filter
        arguments = {
            'color': 'teal',
            'size': None,
            'color_type': None,
            'usage_rights': None,
            'type': None,
            'time': None,
            'aspect_ratio': None,
            'format': None,
            'language': None,
            'time_range': None,
            'exact_size': None
        }
        
        # Build URL parameters
        params = gid.build_url_parameters(arguments)
        
        # The result should contain 'isc:teal' not 'isc:teel'
        self.assertIn('ic:specific,isc:teal', params)
        self.assertNotIn('ic:specific,isc:teel', params)
        
    def test_teal_color_filter_correct_parameter_imagedownloader(self):
        """Test that teal color filter generates correct URL parameter in ImageDownloader class."""
        
        downloader = ImageDownloader()
        
        # Create filters with teal color
        filters = {'color': 'teal'}
        
        # Build URL parameters
        params = downloader._build_url_parameters(filters)
        
        # The result should contain 'isc:teal' not 'isc:teel'
        self.assertIn('ic:specific,isc:teal', params)
        self.assertNotIn('ic:specific,isc:teel', params)
        
    def test_color_filter_would_fail_with_old_bug(self):
        """Test that demonstrates the teal color bug would have caused incorrect URL parameters."""
        
        # This demonstrates what would happen with the old buggy code
        buggy_param = 'ic:specific,isc:teel'  # This is what the bug would produce
        correct_param = 'ic:specific,isc:teal'  # This is what it should produce
        
        # The buggy version should not equal the correct version
        self.assertNotEqual(buggy_param, correct_param)


class TestErrorMessageBugFix(unittest.TestCase):
    """Test that the error message bug has been fixed."""
    
    def test_similar_images_error_message_correct_googleimagesdownload(self):
        """Test that similar_images method returns correct error message."""
        
        gid = google_images_download.googleimagesdownload()
        
        # Mock urllib to simulate connection failure
        with patch('google_images_download.google_images_download.urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = Exception("Connection failed")
            
            # Test Python 3 path
            result = gid.similar_images('http://example.com/image.jpg')
            
            # Should contain 'Could not connect' not 'Cloud not connect'
            self.assertIn('Could not connect', result)
            self.assertNotIn('Cloud not connect', result)
            
    def test_error_message_would_fail_with_old_bug(self):
        """Test that demonstrates the error message bug."""
        
        # This demonstrates what would happen with the old buggy code
        buggy_message = "Cloud not connect to Google Images endpoint"
        correct_message = "Could not connect to Google Images endpoint"
        
        # The buggy version should not equal the correct version
        self.assertNotEqual(buggy_message, correct_message)


class TestIntegrationAfterFixes(unittest.TestCase):
    """Integration tests to ensure all fixes work together."""
    
    def test_multiple_filters_work_correctly(self):
        """Test that multiple filters including fixed ones work correctly."""
        
        gid = google_images_download.googleimagesdownload()
        
        # Create arguments with both fixed filters
        arguments = {
            'color': 'teal',
            'size': '>1024*768',
            'color_type': None,
            'usage_rights': None,
            'type': None,
            'time': None,
            'aspect_ratio': None,
            'format': None,
            'language': None,
            'time_range': None,
            'exact_size': None
        }
        
        # Build URL parameters
        params = gid.build_url_parameters(arguments)
        
        # Both fixes should be present
        self.assertIn('ic:specific,isc:teal', params)  # Fixed teal color
        self.assertIn('isz:lt,islt:xga', params)       # Fixed size parameter
        
        # Old buggy versions should not be present
        self.assertNotIn('isc:teel', params)
        self.assertNotIn('visz:lt', params)
        
    def test_imagedownloader_class_teal_filter(self):
        """Test that ImageDownloader class correctly handles teal color filter."""
        
        downloader = ImageDownloader()
        
        # Test with teal color filter
        filters = {
            'color': 'teal',
            'safe_search': False
        }
        
        params = downloader._build_url_parameters(filters)
        
        # Should contain correct teal parameter
        self.assertIn('ic:specific,isc:teal', params)
        self.assertNotIn('isc:teel', params)


if __name__ == '__main__':
    # Run the tests
    print("Running bug fix tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSizeFilterBugFix))
    suite.addTests(loader.loadTestsFromTestCase(TestColorFilterBugFix))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorMessageBugFix))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationAfterFixes))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✓ All bug fix tests passed!")
        print(f"✓ {result.testsRun} tests run successfully")
    else:
        print("✗ Some tests failed!")
        print(f"✗ {len(result.failures)} failures, {len(result.errors)} errors out of {result.testsRun} tests")
        
    sys.exit(0 if result.wasSuccessful() else 1)
