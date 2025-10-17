#!/usr/bin/env python
# -*- coding: utf-8 -*-
# add a line commenting the purpose of the script

"""
Test script for image_downloader module.
This script demonstrates the programmatic interface functionality.
"""

import os
import sys
from image_downloader import search_images, download_image, ImageDownloader

def test_search_functionality():
    """Test the search_images function."""
    print("Testing image search functionality...")
    
    try:
        # Test basic search
        results = search_images("dogs", limit=5)
        print(f"✓ Found {len(results)} images for 'dogs' query")
        
        # Print first result details
        if results:
            first_result = results[0]
            print(f"  First result:")
            print(f"    URL: {first_result['url'][:60]}...")
            print(f"    Title: {first_result['title'][:50]}...")
            print(f"    Thumbnail: {first_result['thumbnail_url'][:60]}...")
            print(f"    Size: {first_result['width']}x{first_result['height']}")
            print(f"    Format: {first_result['format']}")
        
        # Test with filters
        filtered_results = search_images("cats", limit=3, filters={'color': 'black', 'type': 'photo'})
        print(f"✓ Found {len(filtered_results)} images for 'cats' with black color filter")
        
        return True
        
    except Exception as e:
        print(f"✗ Search test failed: {e}")
        return False

def test_download_functionality():
    """Test the download_image function."""
    print("\nTesting image download functionality...")
    
    try:
        # First, get an image URL from search
        results = search_images("nature", limit=1)
        if not results:
            print("✗ No images found for download test")
            return False
        
        image_url = results[0]['url']
        test_path = "test_downloads/test_image.jpg"
        
        # Download the image
        downloaded_path = download_image(image_url, test_path)
        
        # Check if file was created
        if os.path.exists(downloaded_path):
            file_size = os.path.getsize(downloaded_path)
            print(f"✓ Successfully downloaded image to {downloaded_path}")
            print(f"  File size: {file_size} bytes")
            
            # Clean up test file
            os.remove(downloaded_path)
            os.rmdir("test_downloads")
            print("✓ Test cleanup completed")
            
            return True
        else:
            print("✗ Download failed - file not found")
            return False
        
    except Exception as e:
        print(f"✗ Download test failed: {e}")
        return False

def test_class_interface():
    """Test the ImageDownloader class interface."""
    print("\nTesting ImageDownloader class interface...")
    
    try:
        # Initialize downloader
        downloader = ImageDownloader()
        
        # Test search
        results = downloader.search_images("flowers", limit=2)
        print(f"✓ Class interface search found {len(results)} images")
        
        return True
        
    except Exception as e:
        print(f"✗ Class interface test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Image Downloader Module Tests ===\n")
    
    tests_passed = 0
    total_tests = 3
    
    # Run individual tests
    if test_search_functionality():
        tests_passed += 1
    
    if test_download_functionality():
        tests_passed += 1
    
    if test_class_interface():
        tests_passed += 1
    
    # Summary
    print(f"\n=== Test Results ===")
    print(f"Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! The programmatic interface is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
