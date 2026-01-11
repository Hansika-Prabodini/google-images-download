#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demonstration script showing the bugs before and after fixes.
This script shows what the broken behavior looked like and how it's fixed.
"""

import sys
import os

# Add the modules to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'google_images_download'))

def simulate_old_behavior():
    """Simulate what the old buggy behavior would have produced."""
    print("=== SIMULATING OLD BUGGY BEHAVIOR ===")
    print("(This is what would have happened BEFORE the bug fixes)")
    print()
    
    # Simulate Bug 1: teal -> teel
    print("Bug 1: Teal color mapping")
    print("User requests: color='teal'")
    print("Before fix: Would generate 'ic:specific,isc:teel' (WRONG)")
    print("Expected:   Should generate 'ic:specific,isc:teal' (CORRECT)")
    print("Impact:     Teal color filter would not work - Google wouldn't recognize 'teel'")
    print()
    
    # Simulate Bug 2: isz -> visz
    print("Bug 2: >1024*768 size mapping")
    print("User requests: size='>1024*768'")
    print("Before fix: Would generate 'visz:lt,islt:xga' (WRONG)")
    print("Expected:   Should generate 'isz:lt,islt:xga' (CORRECT)")
    print("Impact:     Size filter would not work - Google wouldn't recognize 'visz:lt'")
    print()

def demonstrate_current_behavior():
    """Demonstrate the current fixed behavior."""
    print("=== DEMONSTRATING CURRENT FIXED BEHAVIOR ===")
    print("(This is what happens AFTER the bug fixes)")
    print()
    
    try:
        from google_images_download import googleimagesdownload
        gid = googleimagesdownload()
        
        # Demonstrate Bug Fix 1: Teal color
        print("Bug Fix 1: Teal color mapping")
        print("User requests: color='teal'")
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
        
        result = gid.build_url_parameters(arguments)
        print(f"After fix:  Generates '{result}'")
        
        if 'ic:specific,isc:teal' in result:
            print("✓ SUCCESS: Contains correct 'teal' parameter")
        else:
            print("✗ ERROR: Does not contain correct 'teal' parameter")
            
        if 'ic:specific,isc:teel' not in result:
            print("✓ SUCCESS: Does not contain incorrect 'teel' parameter")
        else:
            print("✗ ERROR: Still contains incorrect 'teel' parameter")
        print()
        
        # Demonstrate Bug Fix 2: Size parameter
        print("Bug Fix 2: >1024*768 size mapping")
        print("User requests: size='>1024*768'")
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
        
        result = gid.build_url_parameters(arguments)
        print(f"After fix:  Generates '{result}'")
        
        if 'isz:lt,islt:xga' in result:
            print("✓ SUCCESS: Contains correct 'isz:lt' parameter")
        else:
            print("✗ ERROR: Does not contain correct 'isz:lt' parameter")
            
        if 'visz:lt,islt:xga' not in result:
            print("✓ SUCCESS: Does not contain incorrect 'visz:lt' parameter")
        else:
            print("✗ ERROR: Still contains incorrect 'visz:lt' parameter")
        print()
        
    except Exception as e:
        print(f"Error testing google_images_download: {e}")
        return
        
    # Also test image_downloader module
    try:
        from image_downloader import ImageDownloader
        downloader = ImageDownloader()
        
        print("Bug Fix 1 in image_downloader module:")
        print("User requests: filters={'color': 'teal'}")
        
        result = downloader._build_url_parameters({'color': 'teal'})
        print(f"After fix:  Generates '{result}'")
        
        if 'ic:specific,isc:teal' in result:
            print("✓ SUCCESS: Contains correct 'teal' parameter")
        else:
            print("✗ ERROR: Does not contain correct 'teal' parameter")
            
        if 'ic:specific,isc:teel' not in result:
            print("✓ SUCCESS: Does not contain incorrect 'teel' parameter")
        else:
            print("✗ ERROR: Still contains incorrect 'teel' parameter")
        print()
        
    except Exception as e:
        print(f"Error testing image_downloader: {e}")

def demonstrate_complete_url_generation():
    """Show how the fixes affect complete URL generation."""
    print("=== COMPLETE URL GENERATION DEMONSTRATION ===")
    print("Showing how bug fixes affect the complete search URLs")
    print()
    
    try:
        from google_images_download import googleimagesdownload
        gid = googleimagesdownload()
        
        # Generate complete URL with teal color
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
        
        params = gid.build_url_parameters(arguments)
        complete_url = gid.build_search_url("cats", params, None, None, None, False)
        
        print("Complete URL with teal color filter:")
        print(complete_url[:100] + "..." if len(complete_url) > 100 else complete_url)
        print()
        
        if 'ic:specific,isc:teal' in complete_url:
            print("✓ Complete URL contains correct teal parameter")
        else:
            print("✗ Complete URL does not contain correct teal parameter")
            
        # Generate complete URL with size filter
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
        
        params = gid.build_url_parameters(arguments)
        complete_url = gid.build_search_url("dogs", params, None, None, None, False)
        
        print("\nComplete URL with >1024*768 size filter:")
        print(complete_url[:100] + "..." if len(complete_url) > 100 else complete_url)
        print()
        
        if 'isz:lt,islt:xga' in complete_url:
            print("✓ Complete URL contains correct size parameter")
        else:
            print("✗ Complete URL does not contain correct size parameter")
            
    except Exception as e:
        print(f"Error generating complete URLs: {e}")

def main():
    """Main demonstration function."""
    print("BUG FIX DEMONSTRATION")
    print("=" * 50)
    print("This script demonstrates two bugs that were found and fixed:")
    print("1. 'teel' instead of 'teal' in color parameter mapping")
    print("2. 'visz:lt' instead of 'isz:lt' in size parameter mapping")
    print("=" * 50)
    print()
    
    simulate_old_behavior()
    print()
    
    demonstrate_current_behavior()
    print()
    
    demonstrate_complete_url_generation()
    print()
    
    print("=" * 50)
    print("SUMMARY:")
    print("✓ Fixed teal color parameter mapping in both modules")
    print("✓ Fixed >1024*768 size parameter mapping")
    print("✓ These fixes ensure that color and size filters work correctly")
    print("✓ Users can now successfully use 'teal' color and '>1024*768' size filters")

if __name__ == "__main__":
    main()
