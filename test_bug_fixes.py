#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for bug fixes in Google Images Download modules.
These tests specifically target the parameter mapping bugs that were found and fixed.
"""

import unittest
import sys
import os

# Add the modules to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'google_images_download'))
from google_images_download import googleimagesdownload
from image_downloader import ImageDownloader


class TestParameterMappingBugFixes(unittest.TestCase):
    """Test class for parameter mapping bug fixes."""
    
    def setUp(self):
        """Set up test instances."""
        self.gid = googleimagesdownload()
        self.img_downloader = ImageDownloader()
        
    def test_teal_color_parameter_mapping_google_images_download(self):
        """
        Test Bug Fix 1: Verify teal color parameter maps correctly in google_images_download.
        
        This test would have FAILED before the fix because 'teel' was used instead of 'teal'.
        Now it should PASS with the corrected 'teal' parameter.
        """
        # Test arguments with teal color
        arguments = {
            'color': 'teal',
            'size': None,
            'exact_size': None,
            'color_type': None,
            'usage_rights': None,
            'type': None,
            'time': None,
            'time_range': None,
            'aspect_ratio': None,
            'format': None,
            'language': None
        }
        
        # Build URL parameters
        url_params = self.gid.build_url_parameters(arguments)
        
        # Verify that the teal parameter is correctly mapped
        # Should contain 'ic:specific,isc:teal' (not 'teel')
        self.assertIn('ic:specific,isc:teal', url_params, 
                      "Teal color should map to 'ic:specific,isc:teal' parameter")
        
        # Should NOT contain the incorrect 'teel' mapping
        self.assertNotIn('ic:specific,isc:teel', url_params,
                         "Should not contain the incorrect 'teel' parameter")
                         
    def test_size_1024x768_parameter_mapping_google_images_download(self):
        """
        Test Bug Fix 2: Verify >1024*768 size parameter maps correctly in google_images_download.
        
        This test would have FAILED before the fix because 'visz:lt' was used instead of 'isz:lt'.
        Now it should PASS with the corrected 'isz:lt' parameter.
        """
        # Test arguments with >1024*768 size
        arguments = {
            'color': None,
            'size': '>1024*768',
            'exact_size': None,
            'color_type': None,
            'usage_rights': None,
            'type': None,
            'time': None,
            'time_range': None,
            'aspect_ratio': None,
            'format': None,
            'language': None
        }
        
        # Build URL parameters
        url_params = self.gid.build_url_parameters(arguments)
        
        # Verify that the size parameter is correctly mapped
        # Should contain 'isz:lt,islt:xga' (not 'visz:lt,islt:xga')
        self.assertIn('isz:lt,islt:xga', url_params,
                      ">1024*768 size should map to 'isz:lt,islt:xga' parameter")
        
        # Should NOT contain the incorrect 'visz:lt' mapping  
        self.assertNotIn('visz:lt,islt:xga', url_params,
                         "Should not contain the incorrect 'visz:lt' parameter")
    
    def test_teal_color_parameter_mapping_image_downloader(self):
        """
        Test Bug Fix 1: Verify teal color parameter maps correctly in image_downloader.
        
        This test would have FAILED before the fix because 'teel' was used instead of 'teal'.
        Now it should PASS with the corrected 'teal' parameter.
        """
        # Test filters with teal color
        filters = {'color': 'teal'}
        
        # Build URL parameters
        url_params = self.img_downloader._build_url_parameters(filters)
        
        # Verify that the teal parameter is correctly mapped
        # Should contain 'ic:specific,isc:teal' (not 'teel')
        self.assertIn('ic:specific,isc:teal', url_params,
                      "Teal color should map to 'ic:specific,isc:teal' parameter")
        
        # Should NOT contain the incorrect 'teel' mapping
        self.assertNotIn('ic:specific,isc:teel', url_params,
                         "Should not contain the incorrect 'teel' parameter")
    
    def test_complete_url_generation_with_teal_color(self):
        """
        Test complete URL generation with teal color to ensure end-to-end functionality.
        
        This test verifies that the teal color parameter is properly integrated
        into the complete search URL generation process.
        """
        # Test in google_images_download module
        arguments = {
            'color': 'teal',
            'size': None,
            'exact_size': None,
            'color_type': None,
            'usage_rights': None,
            'type': None,
            'time': None,
            'time_range': None,
            'aspect_ratio': None,
            'format': None,
            'language': None
        }
        
        params = self.gid.build_url_parameters(arguments)
        search_url = self.gid.build_search_url("test search", params, None, None, None, False)
        
        # Verify the complete URL contains the correct teal parameter
        self.assertIn('ic:specific,isc:teal', search_url,
                      "Complete URL should contain correct teal color parameter")
        
        # Test in image_downloader module
        filters = {'color': 'teal'}
        params = self.img_downloader._build_url_parameters(filters)
        search_url = self.img_downloader._build_search_url("test search", params, filters)
        
        # Verify the complete URL contains the correct teal parameter
        self.assertIn('ic:specific,isc:teal', search_url,
                      "Complete URL should contain correct teal color parameter")

    def test_complete_url_generation_with_1024x768_size(self):
        """
        Test complete URL generation with >1024*768 size to ensure end-to-end functionality.
        
        This test verifies that the >1024*768 size parameter is properly integrated
        into the complete search URL generation process.
        """
        # Test in google_images_download module
        arguments = {
            'color': None,
            'size': '>1024*768',
            'exact_size': None,
            'color_type': None,
            'usage_rights': None,
            'type': None,
            'time': None,
            'time_range': None,
            'aspect_ratio': None,
            'format': None,
            'language': None
        }
        
        params = self.gid.build_url_parameters(arguments)
        search_url = self.gid.build_search_url("test search", params, None, None, None, False)
        
        # Verify the complete URL contains the correct size parameter
        self.assertIn('isz:lt,islt:xga', search_url,
                      "Complete URL should contain correct >1024*768 size parameter")
                      
    def test_other_colors_still_work_correctly(self):
        """
        Test that other color parameters still work correctly after the teal fix.
        
        This ensures that our fix didn't break anything else.
        """
        test_colors = ['red', 'blue', 'green', 'black', 'white']
        expected_params = ['isc:red', 'isc:blue', 'isc:green', 'isc:black', 'isc:white']
        
        for color, expected_param in zip(test_colors, expected_params):
            with self.subTest(color=color):
                # Test google_images_download
                arguments = {
                    'color': color,
                    'size': None,
                    'exact_size': None,
                    'color_type': None,
                    'usage_rights': None,
                    'type': None,
                    'time': None,
                    'time_range': None,
                    'aspect_ratio': None,
                    'format': None,
                    'language': None
                }
                
                url_params = self.gid.build_url_parameters(arguments)
                self.assertIn(expected_param, url_params,
                              f"{color} color should work correctly")
                
                # Test image_downloader
                filters = {'color': color}
                url_params = self.img_downloader._build_url_parameters(filters)
                self.assertIn(expected_param, url_params,
                              f"{color} color should work correctly in image_downloader")

    def test_other_sizes_still_work_correctly(self):
        """
        Test that other size parameters still work correctly after the >1024*768 fix.
        
        This ensures that our fix didn't break anything else.
        """
        test_sizes = ['>400*300', '>640*480', '>800*600', 'large', 'medium']
        expected_params = ['islt:qsvga', 'islt:vga', 'islt:svga', 'isz:l', 'isz:m']
        
        for size, expected_param in zip(test_sizes, expected_params):
            with self.subTest(size=size):
                arguments = {
                    'color': None,
                    'size': size,
                    'exact_size': None,
                    'color_type': None,
                    'usage_rights': None,
                    'type': None,
                    'time': None,
                    'time_range': None,
                    'aspect_ratio': None,
                    'format': None,
                    'language': None
                }
                
                url_params = self.gid.build_url_parameters(arguments)
                self.assertIn(expected_param, url_params,
                              f"{size} size should work correctly")


class TestBugRegression(unittest.TestCase):
    """Additional regression tests to ensure bugs don't reappear."""
    
    def test_no_teel_in_codebase(self):
        """Verify that 'teel' doesn't appear anywhere in the codebase anymore."""
        import re
        
        # Check google_images_download.py
        with open('google_images_download/google_images_download.py', 'r') as f:
            content = f.read()
        
        # Should not contain 'teel' as a parameter value
        teel_matches = re.findall(r'isc:teel', content)
        self.assertEqual(len(teel_matches), 0, 
                         "google_images_download.py should not contain 'isc:teel'")
        
        # Check image_downloader.py  
        with open('image_downloader.py', 'r') as f:
            content = f.read()
        
        # Should not contain 'teel' as a parameter value
        teel_matches = re.findall(r'isc:teel', content)
        self.assertEqual(len(teel_matches), 0,
                         "image_downloader.py should not contain 'isc:teel'")
                         
    def test_no_visz_in_codebase(self):
        """Verify that 'visz' doesn't appear anywhere in the codebase anymore."""
        import re
        
        # Check google_images_download.py
        with open('google_images_download/google_images_download.py', 'r') as f:
            content = f.read()
        
        # Should not contain 'visz:lt'
        visz_matches = re.findall(r'visz:lt', content) 
        self.assertEqual(len(visz_matches), 0,
                         "google_images_download.py should not contain 'visz:lt'")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
