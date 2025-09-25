#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple verification script to confirm our bug fixes work correctly.
This demonstrates that the typos have been fixed.
"""

import sys
import os

# Add the google_images_download directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'google_images_download'))
from google_images_download import googleimagesdownload
from image_downloader import ImageDownloader

def test_teal_color_fix():
    """Test that teal color mapping is correct."""
    print("Testing teal color parameter fix...")
    
    # Test original module
    downloader = googleimagesdownload()
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
    
    url_params = downloader.build_url_parameters(test_arguments)
    
    # Check that the correct mapping is present
    if 'ic:specific,isc:teal' in url_params:
        print("✓ Original module: teal color parameter is correct")
    else:
        print("✗ Original module: teal color parameter is incorrect")
        print(f"URL params: {url_params}")
    
    # Check that the bug (incorrect mapping) is NOT present
    if 'ic:specific,isc:teel' not in url_params:
        print("✓ Original module: incorrect 'teel' parameter is NOT present")
    else:
        print("✗ Original module: found incorrect 'teel' parameter")
    
    # Test new image_downloader module
    new_downloader = ImageDownloader()
    test_filters = {'color': 'teal'}
    
    new_url_params = new_downloader._build_url_parameters(test_filters)
    
    if 'ic:specific,isc:teal' in new_url_params:
        print("✓ New module: teal color parameter is correct")
    else:
        print("✗ New module: teal color parameter is incorrect")
        print(f"URL params: {new_url_params}")

def test_large_size_fix():
    """Test that >1024*768 size mapping is correct."""
    print("\nTesting >1024*768 size parameter fix...")
    
    # Test original module
    downloader = googleimagesdownload()
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
    
    url_params = downloader.build_url_parameters(test_arguments)
    
    # Check that the correct mapping is present
    if 'isz:lt,islt:xga' in url_params:
        print("✓ Original module: >1024*768 size parameter is correct")
    else:
        print("✗ Original module: >1024*768 size parameter is incorrect")
        print(f"URL params: {url_params}")
    
    # Check that the bug (incorrect mapping) is NOT present
    if 'visz:lt,islt:xga' not in url_params:
        print("✓ Original module: incorrect 'visz' parameter is NOT present")
    else:
        print("✗ Original module: found incorrect 'visz' parameter")

def test_combined_parameters():
    """Test that both fixes work together."""
    print("\nTesting combined teal color + >1024*768 size parameters...")
    
    downloader = googleimagesdownload()
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
    
    url_params = downloader.build_url_parameters(test_arguments)
    print(f"Combined URL params: {url_params}")
    
    # Check that both correct parameters are present
    teal_correct = 'ic:specific,isc:teal' in url_params
    size_correct = 'isz:lt,islt:xga' in url_params
    
    # Check that neither incorrect parameter is present
    teal_bug_absent = 'ic:specific,isc:teel' not in url_params
    size_bug_absent = 'visz:lt,islt:xga' not in url_params
    
    if teal_correct and size_correct and teal_bug_absent and size_bug_absent:
        print("✓ All parameters are correct! Both bugs have been fixed.")
    else:
        print("✗ Some parameters are incorrect:")
        if not teal_correct:
            print("  - Teal color parameter is wrong")
        if not size_correct:
            print("  - Size parameter is wrong")
        if not teal_bug_absent:
            print("  - Found incorrect 'teel' parameter")
        if not size_bug_absent:
            print("  - Found incorrect 'visz' parameter")

def main():
    print("=== Bug Fix Verification ===")
    print("Testing that the parameter mapping typos have been fixed.\n")
    
    test_teal_color_fix()
    test_large_size_fix() 
    test_combined_parameters()
    
    print("\n=== Verification Complete ===")

if __name__ == '__main__':
    main()
