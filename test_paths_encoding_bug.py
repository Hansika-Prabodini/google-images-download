#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit test for the paths encoding bug in google_images_download.py

This test demonstrates a bug where the code tries to encode a dictionary as if it were a string,
which causes an AttributeError when print_paths is True.

The bug occurred on lines 820, 830, and 839 in google_images_download.py where:
    print(paths.encode('raw_unicode_escape').decode('utf-8'))

Should be:
    print(str(paths).encode('raw_unicode_escape').decode('utf-8'))

Because 'paths' is a dictionary, not a string.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the google_images_download module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'google_images_download'))

from google_images_download import google_images_download


class TestPathsEncodingBug(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.downloader = google_images_download.googleimagesdownload()
    
    def test_paths_encoding_bug_fixed(self):
        """
        Test that verifies the paths encoding bug is fixed.
        
        This test verifies that when print_paths is True, the code properly
        converts the dictionary to string before encoding, rather than trying
        to encode the dictionary directly which would cause AttributeError.
        """
        # Create test arguments that would have triggered the bug
        arguments = {
            'keywords': 'test',
            'limit': 1,
            'print_paths': True,  # This triggers the code path that had the bug
            'silent_mode': False,
            'no_download': True,  # Prevent actual downloading for testing
            'output_directory': None,
            'image_directory': None,
            'no_directory': False,
            'thumbnail': False,
            'thumbnail_only': False,
            'extract_metadata': False,
            'related_images': False,
            'chromedriver': None,
            'prefix_keywords': None,
            'suffix_keywords': None,
            'keywords_from_file': None,
            'single_image': None,
            'url': None,
            'similar_images': None,
            'time': None,
            'time_range': None,
            'size': None,
            'exact_size': None,
            'color': None,
            'safe_search': False,
            'specific_site': None
        }
        
        # Mock the download_page method to return fake HTML containing valid image metadata
        fake_html = '''
        <div class="rg_meta notranslate">{"ou":"http://example.com/image1.jpg","ity":"jpg","oh":100,"ow":100,"pt":"Test Image","rh":"example.com","ru":"http://example.com","tu":"http://example.com/thumb1.jpg"}</div>
        '''
        
        with patch.object(self.downloader, 'download_page', return_value=fake_html):
            with patch.object(self.downloader, 'create_directories'):
                with patch('builtins.print') as mock_print:
                    try:
                        # This should NOT raise an AttributeError after the patch
                        paths, errors = self.downloader.download(arguments)
                        
                        # Verify that the function completes successfully
                        self.assertIsInstance(paths, dict, "Expected paths to be a dictionary")
                        self.assertIsInstance(errors, int, "Expected errors to be an integer")
                        
                        # Verify that print was called with the encoded dictionary string
                        # This would have failed before the patch with AttributeError
                        mock_print.assert_called()
                        
                        # Get the print calls and verify at least one was about paths
                        print_calls = [str(call) for call in mock_print.call_args_list]
                        paths_printed = any("test" in call for call in print_calls)
                        self.assertTrue(paths_printed, "Expected paths to be printed")
                        
                        print("✓ Test passed: The paths encoding bug has been successfully fixed!")
                        
                    except AttributeError as e:
                        if "'dict' object has no attribute 'encode'" in str(e):
                            self.fail(f"The paths encoding bug still exists: {e}")
                        else:
                            # If it's a different AttributeError, re-raise it
                            raise
                    except Exception as e:
                        # For other exceptions, provide context
                        self.fail(f"Unexpected error during test: {e}")


class TestPathsEncodingBugSimulation(unittest.TestCase):
    """
    Additional test that simulates the exact bug scenario
    """
    
    def test_dictionary_encoding_directly(self):
        """
        Test that demonstrates what the bug was about by simulating the exact scenario.
        
        This test shows that trying to encode a dictionary directly fails,
        but encoding str(dictionary) works fine.
        """
        # Simulate the paths dictionary that would be returned
        test_paths = {'test': ['/path/to/image1.jpg', '/path/to/image2.jpg']}
        
        # This would have caused the bug - trying to encode dictionary directly
        with self.assertRaises(AttributeError) as context:
            test_paths.encode('raw_unicode_escape').decode('utf-8')
        
        self.assertIn("'dict' object has no attribute 'encode'", str(context.exception))
        
        # This is the fix - convert to string first, then encode
        try:
            result = str(test_paths).encode('raw_unicode_escape').decode('utf-8')
            self.assertIsInstance(result, str)
            self.assertIn('test', result)  # Verify the dictionary content is in the string
            print("✓ Test passed: String conversion before encoding works correctly!")
        except Exception as e:
            self.fail(f"The fix should work but got error: {e}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
