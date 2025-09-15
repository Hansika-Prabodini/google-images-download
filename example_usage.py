#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example usage of the image_downloader module.
This demonstrates how to use the programmatic interface for Flask applications.
"""

import os
from image_downloader import search_images, download_image, ImageDownloader

def example_basic_search():
    """Basic image search example."""
    print("=== Basic Image Search ===")
    
    # Search for images
    results = search_images("puppies", limit=5)
    
    print(f"Found {len(results)} images:")
    for i, image in enumerate(results, 1):
        print(f"  {i}. {image['title'][:50]}...")
        print(f"     URL: {image['url']}")
        print(f"     Size: {image['width']}x{image['height']}")
        print()

def example_filtered_search():
    """Search with filters example."""
    print("=== Filtered Image Search ===")
    
    # Search with specific filters
    filters = {
        'color': 'blue',
        'type': 'photo',
        'size': 'large',
        'safe_search': True
    }
    
    results = search_images("ocean", limit=3, filters=filters)
    
    print(f"Found {len(results)} blue ocean photos:")
    for image in results:
        print(f"  - {image['title']}")
        print(f"    {image['width']}x{image['height']} {image['format']}")

def example_download_images():
    """Download images example."""
    print("=== Download Images ===")
    
    # Create downloads directory
    os.makedirs("downloads", exist_ok=True)
    
    # Search for images to download
    results = search_images("nature landscapes", limit=2)
    
    for i, image in enumerate(results, 1):
        try:
            # Determine file extension
            format_ext = image['format'].lower() if image['format'] else 'jpg'
            filename = f"downloads/nature_image_{i}.{format_ext}"
            
            # Download the image
            downloaded_path = download_image(image['url'], filename)
            print(f"✓ Downloaded: {downloaded_path}")
            
        except Exception as e:
            print(f"✗ Failed to download image {i}: {e}")

def example_class_usage():
    """Using the ImageDownloader class directly."""
    print("=== Using ImageDownloader Class ===")
    
    # Initialize with custom chromedriver path if needed
    downloader = ImageDownloader()
    
    # Search for images
    results = downloader.search_images("mountains", limit=3)
    
    print(f"Class interface found {len(results)} mountain images")
    
    # Download first image if available
    if results:
        try:
            filename = "downloads/mountain_example.jpg"
            downloader.download_image(results[0]['url'], filename)
            print(f"✓ Downloaded example image to {filename}")
        except Exception as e:
            print(f"✗ Download failed: {e}")

def flask_integration_example():
    """Example of how this might be used in a Flask application."""
    print("=== Flask Integration Example ===")
    
    # This simulates what a Flask route might do
    def search_endpoint(query, limit=10):
        """Simulated Flask endpoint for image search."""
        try:
            results = search_images(query, limit=limit)
            
            # Format for JSON response
            response_data = {
                'success': True,
                'count': len(results),
                'images': []
            }
            
            for image in results:
                response_data['images'].append({
                    'url': image['url'],
                    'thumbnail_url': image['thumbnail_url'],
                    'title': image['title'],
                    'width': image['width'],
                    'height': image['height']
                })
            
            return response_data
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Simulate API call
    response = search_endpoint("cats", limit=3)
    print(f"API Response: Found {response.get('count', 0)} images")
    print(f"Success: {response['success']}")

if __name__ == "__main__":
    print("Image Downloader Module - Usage Examples\n")
    
    try:
        example_basic_search()
        print("\n" + "="*50 + "\n")
        
        example_filtered_search()
        print("\n" + "="*50 + "\n")
        
        example_download_images()
        print("\n" + "="*50 + "\n")
        
        example_class_usage()
        print("\n" + "="*50 + "\n")
        
        flask_integration_example()
        
        print("\n✓ All examples completed successfully!")
        
    except Exception as e:
        print(f"✗ Example failed: {e}")
        print("\nNote: Make sure you have all required dependencies installed:")
        print("pip install selenium webdriver-manager requests")
