#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example usage of the image_downloader module.
This demonstrates how to use the programmatic interface for Flask applications.
"""

import os
from typing import Dict, List, Any
from image_downloader import search_images, download_image, ImageDownloader

# ---- Helpers ----

def _safe_text(value: Any, default: str = "") -> str:
    """Return a safe string representation, avoiding None-related errors."""
    if value is None:
        return default
    try:
        return str(value)
    except Exception:
        return default


def _ensure_downloads_dir() -> None:
    """Ensure the downloads directory exists."""
    os.makedirs("downloads", exist_ok=True)


def example_basic_search() -> None:
    """Basic image search example."""
    print("=== Basic Image Search ===")
    
    # Search for images
    results = search_images("puppies", limit=5)
    
    print(f"Found {len(results)} images:")
    for i, image in enumerate(results, 1):
        title = _safe_text(image.get('title'))[:50]
        url = image.get('url') or ''
        width = image.get('width') or 0
        height = image.get('height') or 0
        print(f"  {i}. {title}...")
        print(f"     URL: {url}")
        print(f"     Size: {width}x{height}")
        print()


def example_filtered_search() -> None:
    """Search with filters example."""
    print("=== Filtered Image Search ===")
    
    # Search with specific filters
    filters: Dict[str, Any] = {
        'color': 'blue',
        'type': 'photo',
        'size': 'large',
        'safe_search': True
    }
    
    results = search_images("ocean", limit=3, filters=filters)
    
    print(f"Found {len(results)} blue ocean photos:")
    for image in results:
        title = _safe_text(image.get('title'))
        width = image.get('width') or 0
        height = image.get('height') or 0
        img_format = _safe_text(image.get('format') or '')
        print(f"  - {title}")
        print(f"    {width}x{height} {img_format}")


def example_download_images() -> None:
    """Download images example."""
    print("=== Download Images ===")
    
    # Ensure downloads directory
    _ensure_downloads_dir()
    
    # Search for images to download
    results = search_images("nature landscapes", limit=2)
    
    for i, image in enumerate(results, 1):
        try:
            # Determine file extension
            img_format = image.get('format')
            format_ext = img_format.lower() if isinstance(img_format, str) and img_format else 'jpg'
            filename = f"downloads/nature_image_{i}.{format_ext}"
            
            # Download the image
            image_url = image.get('url') or ''
            downloaded_path = download_image(image_url, filename)
            print(f"✓ Downloaded: {downloaded_path}")
            
        except Exception as e:
            print(f"✗ Failed to download image {i}: {e}")


def example_class_usage() -> None:
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
            _ensure_downloads_dir()
            filename = "downloads/mountain_example.jpg"
            first_url = results[0].get('url') or ''
            downloader.download_image(first_url, filename)
            print(f"✓ Downloaded example image to {filename}")
        except Exception as e:
            print(f"✗ Download failed: {e}")


def flask_integration_example() -> None:
    """Example of how this might be used in a Flask application."""
    print("=== Flask Integration Example ===")
    
    # This simulates what a Flask route might do
    def search_endpoint(query: str, limit: int = 10) -> Dict[str, Any]:
        """Simulated Flask endpoint for image search."""
        try:
            results = search_images(query, limit=limit)
            
            # Format for JSON response
            response_data: Dict[str, Any] = {
                'success': True,
                'count': len(results),
                'images': []
            }
            
            for image in results:
                response_data['images'].append({
                    'url': image.get('url'),
                    'thumbnail_url': image.get('thumbnail_url'),
                    'title': image.get('title'),
                    'width': image.get('width'),
                    'height': image.get('height')
                })
            
            return response_data
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Simulate API call
    response = search_endpoint("cats", limit=3)
    print(f"API Response: Found {response.get('count', 0)} images")
    print(f"Success: {response['success']}")


def main() -> None:
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


if __name__ == "__main__":
    main()