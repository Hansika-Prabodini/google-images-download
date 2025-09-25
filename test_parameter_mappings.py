#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for parameter mapping bugs.

This test module checks that the color and size parameter mappings 
are correct in both the original google_images_download module and 
the image_downloader module.
"""

import unittest
import sys
import os

# Add the google_images_download directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'google_images_download'))
from google_images_download import googleimagesdownload
from image_downloader import ImageDownloader


class TestParameterMappings(unittest.TestCase):
    """Test parameter mapping corrections."""

    def setUp(self):
        """Set up test instances."""
        self.original_downloader = googleimagesdownload()
        self.new_downloader = ImageDownloader()

    def test_teal_color_mapping_original(self):
        """Test that 'teal' color maps to correct Google search parameter in original module."""
        # Create test arguments with teal color
        test_arguments = {
            'color': 'teal',
            'color_type': None,
            'usage_rights': None,
            'size': None,
            'type': None,
            'time': None,
            'aspect_ratio': None,
            'format': None,
            'language': None,
            'time_range': None,
            'exact_size': None
        }
        
        # Build URL parameters
        url_params = self.original_downloader.build_url_parameters(test_arguments)
        
        # The correct mapping should be 'ic:specific,isc:teal', not 'ic:specific,isc:teel'
        expected_teal_param = 'ic:specific,isc:teal'
        incorrect_teal_param = 'ic:specific,isc:teel'  # The bug we fixed
        
        self.assertIn(expected_teal_param, url_params, 
                     f"Expected teal color parameter '{expected_teal_param}' not found in URL params: {url_params}")
        self.assertNotIn(incorrect_teal_param, url_params,
                        f"Found incorrect teal parameter '{incorrect_teal_param}' in URL params: {url_params}")

    def test_large_size_mapping_original(self):
        """Test that '>1024*768' size maps to correct Google search parameter in original module."""
        # Create test arguments with >1024*768 size
        test_arguments = {
            'color': None,
            'color_type': None,
            'usage_rights': None,
            'size': '>1024*768',
            'type': None,
            'time': None,
            'aspect_ratio': None,
            'format': None,
            'language': None,
            'time_range': None,
            'exact_size': None
        }
        
        # Build URL parameters
        url_params = self.original_downloader.build_url_parameters(test_arguments)
        
        # The correct mapping should be 'isz:lt,islt:xga', not 'visz:lt,islt:xga'
        expected_size_param = 'isz:lt,islt:xga'
        incorrect_size_param = 'visz:lt,islt:xga'  # The bug we fixed
        
        self.assertIn(expected_size_param, url_params,
                     f"Expected size parameter '{expected_size_param}' not found in URL params: {url_params}")
        self.assertNotIn(incorrect_size_param, url_params,
                        f"Found incorrect size parameter '{incorrect_size_param}' in URL params: {url_params}")

    def test_teal_color_mapping_new_module(self):
        """Test that 'teal' color maps correctly in the new image_downloader module."""
        # Create test filters with teal color
        test_filters = {'color': 'teal'}
        
        # Build URL parameters
        url_params = self.new_downloader._build_url_parameters(test_filters)
        
        # The correct mapping should be 'ic:specific,isc:teal'
        expected_teal_param = 'ic:specific,isc:teal'
        incorrect_teal_param = 'ic:specific,isc:teel'  # The bug we fixed
        
        self.assertIn(expected_teal_param, url_params,
                     f"Expected teal color parameter '{expected_teal_param}' not found in URL params: {url_params}")
        self.assertNotIn(incorrect_teal_param, url_params,
                        f"Found incorrect teal parameter '{incorrect_teal_param}' in URL params: {url_params}")

    def test_combined_parameters(self):
        """Test that both teal color and >1024*768 size work together correctly."""
        # Test original module
        test_arguments = {
            'color': 'teal',
            'color_type': None,
            'usage_rights': None,
            'size': '>1024*768',
            'type': None,
            'time': None,
            'aspect_ratio': None,
            'format': None,
            'language': None,
            'time_range': None,
            'exact_size': None
        }
        
        url_params = self.original_downloader.build_url_parameters(test_arguments)
        
        # Both parameters should be present and correct
        self.assertIn('ic:specific,isc:teal', url_params,
                     "Teal color parameter not found in combined test")
        self.assertIn('isz:lt,islt:xga', url_params,
                     "Large size parameter not found in combined test")
        
        # Neither incorrect parameter should be present
        self.assertNotIn('ic:specific,isc:teel', url_params,
                        "Found incorrect teal parameter in combined test")
        self.assertNotIn('visz:lt,islt:xga', url_params,
                        "Found incorrect size parameter in combined test")

    def test_url_parameter_format(self):
        """Test that URL parameters are formatted correctly."""
        test_arguments = {
            'color': 'teal',
            'color_type': None,
            'usage_rights': None,
            'size': '>1024*768',
            'type': None,
            'time': None,
            'aspect_ratio': None,
            'format': None,
            'language': None,
            'time_range': None,
            'exact_size': None
        }
        
        url_params = self.original_downloader.build_url_parameters(test_arguments)
        
        # Should start with &tbs=
        self.assertTrue(url_params.startswith('&tbs='),
                       f"URL params should start with '&tbs=' but got: {url_params}")
        
        # Should contain comma-separated parameters
        if ',' in url_params:
            # Multiple parameters should be comma-separated
            parts = url_params[5:].split(',')  # Remove '&tbs=' prefix
            self.assertGreater(len(parts), 1, "Expected multiple comma-separated parameters")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
