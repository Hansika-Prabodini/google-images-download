#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for image_downloader module.

Purpose:
- Acts as a minimal, runnable smoke test for the programmatic API exposed by image_downloader.py.
- Shows both the functional helpers (search_images, download_image) and the class-based interface (ImageDownloader).

How to run:
- Ensure you have an active internet connection (the tests perform live searches/downloads).
- Run:  python test_image_downloader.py
- Exit code 0 means all tests passed; non‑zero means at least one test failed.
"""

import os
import sys
from image_downloader import search_images, download_image, ImageDownloader

def test_search_functionality():
    """Test the search_images function by performing small, network-backed queries."""
    print("Testing image search functionality...")
    
    try:
        # Perform a small search to keep runtime and network usage low.
        # The function returns a list of metadata dicts (no files are downloaded here).
        results = search_images("dogs", limit=5)
        print(f"✓ search_images('dogs', limit=5) returned {len(results)} result(s)")
        
        # Print details from the first result to illustrate the schema we return.
        if results:
            first_result = results[0]
            print("  First result (truncated for display):")
            print(f"    URL: {first_result['url'][:60]}...")
            print(f"    Title: {first_result['title'][:50]}...")
            print(f"    Thumbnail: {first_result['thumbnail_url'][:60]}...")
            print(f"    Size: {first_result['width']}x{first_result['height']}")
            print(f"    Format: {first_result['format']}")
        
        # Demonstrate use of optional filters: here we ask for black photos of cats.
        filtered_results = search_images(
            "cats",
            limit=3,
            filters={"color": "black", "type": "photo"},
        )
        print(
            f"✓ search_images('cats', limit=3, filters={{'color': 'black', 'type': 'photo'}}) returned {len(filtered_results)} result(s)"
        )
        
        # If we reached here without exceptions, consider the test successful.
        return True
        
    except Exception as e:
        # Any exception means the search path is not functioning as expected.
        print(f"✗ Search test failed: {e}")
        return False

def test_download_functionality():
    """
    Test the download_image function end-to-end by:
    1) Searching for a single image to get a valid direct URL.
    2) Downloading that image to a temporary folder.
    3) Best‑effort cleanup of the downloaded artifact and its directory.
    Success is defined as the file being created without raising exceptions.
    """
    print("\nTesting image download functionality...")
    
    try:
        # Obtain a valid, reachable image URL via the search helper.
        results = search_images("nature", limit=1)
        if not results:
            print("✗ No images found for download test")
            return False
        
        image_url = results[0]["url"]
        # Use a dedicated subdirectory so cleanup is straightforward and isolated.
        test_path = "test_downloads/test_image.jpg"
        
        # Attempt the download. The function creates parent directories as needed.
        downloaded_path = download_image(image_url, test_path)
        
        # Validate that the file was created and provide basic telemetry.
        if os.path.exists(downloaded_path):
            file_size = os.path.getsize(downloaded_path)
            print(f"✓ Downloaded image to {downloaded_path}")
            print(f"  File size: {file_size} bytes")
            
            # Clean up the test artifact. Cleanup is best‑effort because some
            # environments (e.g., CI on Windows) may hold file handles briefly.
            try:
                os.remove(downloaded_path)
            except OSError as e:
                print(f"⚠ Warning: Failed to remove test file: {e}")
            
            # Attempt to remove the test directory as well (it should now be empty).
            try:
                os.rmdir("test_downloads")
            except OSError as e:
                print(f"⚠ Warning: Failed to remove test directory: {e}")
            else:
                print("✓ Test artifacts cleaned up")
            
            return True
        else:
            print("✗ Download failed - file not found after download_image returned")
            return False
        
    except Exception as e:
        print(f"✗ Download test failed: {e}")
        return False

def test_class_interface():
    """
    Test the class-based interface (ImageDownloader), which exposes the same
    capabilities as the functional helpers but allows configuration/state to be
    associated with an instance (e.g., chromedriver_path for extended searches).
    """
    print("\nTesting ImageDownloader class interface...")
    
    try:
        # Initialize the downloader instance. No special configuration is needed
        # for these tests, but a path to chromedriver could be provided here.
        downloader = ImageDownloader()
        
        # Call the instance method to ensure parity with the module-level helper.
        results = downloader.search_images("flowers", limit=2)
        print(f"✓ ImageDownloader.search_images('flowers', limit=2) returned {len(results)} result(s)")
        
        return True
        
    except Exception as e:
        print(f"✗ Class interface test failed: {e}")
        return False

def main():
    """Run all tests and aggregate a simple pass/fail summary."""
    print("=== Image Downloader: Programmatic API Tests ===\n")
    
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
    print("\n=== Test Results ===")
    print(f"Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! The programmatic interface is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
