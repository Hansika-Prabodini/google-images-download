#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple verification script to test that the bug fixes work correctly.
This script tests the specific bug fixes without requiring external dependencies.
"""

import sys
import os

# Add the modules to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'google_images_download'))

def test_google_images_download_fixes():
    """Test the fixes in google_images_download module."""
    print("Testing google_images_download fixes...")
    
    from google_images_download import googleimagesdownload
    gid = googleimagesdownload()
    
    # Test Bug Fix 1: Teal color parameter
    print("\n1. Testing teal color parameter fix...")
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
    
    url_params = gid.build_url_parameters(arguments)
    print(f"Generated URL parameters: {url_params}")
    
    if 'ic:specific,isc:teal' in url_params:
        print("✓ PASS: Teal color maps correctly to 'ic:specific,isc:teal'")
    else:
        print("✗ FAIL: Teal color does not map correctly")
        return False
        
    if 'ic:specific,isc:teel' in url_params:
        print("✗ FAIL: Still contains incorrect 'teel' mapping")
        return False
    else:
        print("✓ PASS: Does not contain incorrect 'teel' mapping")
    
    # Test Bug Fix 2: >1024*768 size parameter
    print("\n2. Testing >1024*768 size parameter fix...")
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
    
    url_params = gid.build_url_parameters(arguments)
    print(f"Generated URL parameters: {url_params}")
    
    if 'isz:lt,islt:xga' in url_params:
        print("✓ PASS: >1024*768 size maps correctly to 'isz:lt,islt:xga'")
    else:
        print("✗ FAIL: >1024*768 size does not map correctly")
        return False
        
    if 'visz:lt,islt:xga' in url_params:
        print("✗ FAIL: Still contains incorrect 'visz:lt' mapping")
        return False
    else:
        print("✓ PASS: Does not contain incorrect 'visz:lt' mapping")
    
    return True

def test_image_downloader_fixes():
    """Test the fixes in image_downloader module."""
    print("\n\nTesting image_downloader fixes...")
    
    try:
        from image_downloader import ImageDownloader
        downloader = ImageDownloader()
        
        # Test Bug Fix 1: Teal color parameter in image_downloader
        print("\n3. Testing teal color parameter fix in image_downloader...")
        filters = {'color': 'teal'}
        
        url_params = downloader._build_url_parameters(filters)
        print(f"Generated URL parameters: {url_params}")
        
        if 'ic:specific,isc:teal' in url_params:
            print("✓ PASS: Teal color maps correctly to 'ic:specific,isc:teal'")
        else:
            print("✗ FAIL: Teal color does not map correctly")
            return False
            
        if 'ic:specific,isc:teel' in url_params:
            print("✗ FAIL: Still contains incorrect 'teel' mapping")
            return False
        else:
            print("✓ PASS: Does not contain incorrect 'teel' mapping")
        
        return True
        
    except ImportError as e:
        print(f"Could not import image_downloader: {e}")
        return False

def test_code_contains_fixes():
    """Test that the source code contains the fixes."""
    print("\n\nTesting that source code contains the fixes...")
    
    # Check google_images_download.py
    print("\n4. Checking google_images_download.py source code...")
    try:
        with open('google_images_download/google_images_download.py', 'r') as f:
            content = f.read()
        
        if 'ic:specific,isc:teal' in content:
            print("✓ PASS: google_images_download.py contains correct 'teal' mapping")
        else:
            print("✗ FAIL: google_images_download.py does not contain correct 'teal' mapping")
            
        if 'ic:specific,isc:teel' in content:
            print("✗ FAIL: google_images_download.py still contains incorrect 'teel' mapping")
        else:
            print("✓ PASS: google_images_download.py does not contain incorrect 'teel' mapping")
            
        if 'isz:lt,islt:xga' in content:
            print("✓ PASS: google_images_download.py contains correct size mapping")
        else:
            print("✗ FAIL: google_images_download.py does not contain correct size mapping")
            
        if 'visz:lt,islt:xga' in content:
            print("✗ FAIL: google_images_download.py still contains incorrect 'visz:lt' mapping")
        else:
            print("✓ PASS: google_images_download.py does not contain incorrect 'visz:lt' mapping")
            
    except FileNotFoundError:
        print("✗ FAIL: Could not find google_images_download.py")
        return False
    
    # Check image_downloader.py
    print("\n5. Checking image_downloader.py source code...")
    try:
        with open('image_downloader.py', 'r') as f:
            content = f.read()
        
        if 'ic:specific,isc:teal' in content:
            print("✓ PASS: image_downloader.py contains correct 'teal' mapping")
        else:
            print("✗ FAIL: image_downloader.py does not contain correct 'teal' mapping")
            
        if 'ic:specific,isc:teel' in content:
            print("✗ FAIL: image_downloader.py still contains incorrect 'teel' mapping")
            return False
        else:
            print("✓ PASS: image_downloader.py does not contain incorrect 'teel' mapping")
            
    except FileNotFoundError:
        print("✗ FAIL: Could not find image_downloader.py")
        return False
    
    return True

def main():
    """Run all verification tests."""
    print("=== Bug Fix Verification Tests ===")
    print("This script verifies that the identified bugs have been fixed:")
    print("1. Bug: 'teel' instead of 'teal' in color parameter mapping")
    print("2. Bug: 'visz:lt' instead of 'isz:lt' in size parameter mapping")
    print("="*50)
    
    all_tests_passed = True
    
    # Test the fixes work functionally
    if not test_google_images_download_fixes():
        all_tests_passed = False
    
    if not test_image_downloader_fixes():
        all_tests_passed = False
        
    # Test the source code contains the fixes
    if not test_code_contains_fixes():
        all_tests_passed = False
    
    print("\n" + "="*50)
    if all_tests_passed:
        print("✓ ALL TESTS PASSED: Bug fixes are working correctly!")
        print("\nSummary of fixes:")
        print("- Fixed 'teel' -> 'teal' in both modules")
        print("- Fixed 'visz:lt' -> 'isz:lt' in google_images_download.py")
        print("\nThese bugs would have caused:")
        print("- Teal color filter to not work properly")
        print("- >1024*768 size filter to generate malformed parameters")
        return True
    else:
        print("✗ SOME TESTS FAILED: Bug fixes may not be working correctly!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
