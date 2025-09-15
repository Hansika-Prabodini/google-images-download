# Programmatic Interface for Image Downloader

This document describes the new programmatic interface for the image download functionality, designed to be used in web applications like Flask.

## Overview

The `image_downloader.py` module provides a clean Python API for searching and downloading images from Google Images, without requiring command-line arguments.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

The following packages will be installed:
- `selenium>=4.0.0` - For web scraping with headless browser
- `webdriver-manager>=3.8.0` - For automatic Chrome WebDriver management
- `requests>=2.28.0` - For HTTP requests

## Quick Start

### Simple Image Search

```python
from image_downloader import search_images

# Search for images
results = search_images("dogs", limit=10)

for image in results:
    print(f"Title: {image['title']}")
    print(f"URL: {image['url']}")
    print(f"Size: {image['width']}x{image['height']}")
```

### Search with Filters

```python
from image_downloader import search_images

# Search with specific filters
filters = {
    'color': 'blue',
    'type': 'photo',
    'size': 'large',
    'safe_search': True
}

results = search_images("ocean", limit=5, filters=filters)
```

### Download Images

```python
from image_downloader import download_image

# Download a single image
image_url = "https://example.com/image.jpg"
local_path = "downloads/my_image.jpg"

downloaded_path = download_image(image_url, local_path)
print(f"Downloaded to: {downloaded_path}")
```

### Class-based Usage

```python
from image_downloader import ImageDownloader

# Initialize with optional chromedriver path
downloader = ImageDownloader(chromedriver_path="/path/to/chromedriver")

# Search for images
results = downloader.search_images("nature", limit=20)

# Download an image
downloader.download_image("https://example.com/image.jpg", "local_image.jpg")
```

## API Reference

### `search_images(query, limit=10, filters=None, chromedriver_path=None)`

Search for images and return metadata.

**Parameters:**
- `query` (str): Search term
- `limit` (int): Number of images to find (default: 10, max recommended: 100)
- `filters` (dict, optional): Search filters
- `chromedriver_path` (str, optional): Path to chromedriver executable

**Returns:**
- List of dictionaries with image metadata

**Example filters:**
```python
filters = {
    'color': 'red',           # red, orange, yellow, green, teal, blue, purple, pink, white, gray, black, brown
    'color_type': 'full-color',  # full-color, black-and-white, transparent
    'size': 'large',          # large, medium, icon, >400*300, >640*480, etc.
    'type': 'photo',          # face, photo, clipart, line-drawing, animated
    'format': 'jpg',          # jpg, gif, png, bmp, svg, webp, ico
    'time': 'past-month',     # past-24-hours, past-7-days, past-month, past-year
    'safe_search': True       # Enable safe search
}
```

**Return structure:**
Each image dict contains:
```python
{
    'url': 'https://example.com/image.jpg',
    'thumbnail_url': 'https://example.com/thumb.jpg',
    'title': 'Image description',
    'source': 'https://example.com/page',
    'width': 800,
    'height': 600,
    'format': 'jpg',
    'host': 'example.com'
}
```

### `download_image(image_url, destination_path, timeout=10)`

Download a single image from URL.

**Parameters:**
- `image_url` (str): Direct URL to the image
- `destination_path` (str): Local file path where image should be saved
- `timeout` (int): Download timeout in seconds (default: 10)

**Returns:**
- str: Path to the downloaded file

### `ImageDownloader` Class

Class-based interface for more control.

**Constructor:**
```python
ImageDownloader(chromedriver_path=None)
```

**Methods:**
- `search_images(query, limit=10, filters=None)` - Search for images
- `download_image(image_url, destination_path, timeout=10)` - Download image

## Flask Integration Example

```python
from flask import Flask, jsonify, request
from image_downloader import search_images

app = Flask(__name__)

@app.route('/api/search')
def search_endpoint():
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    
    try:
        results = search_images(query, limit=limit)
        return jsonify({
            'success': True,
            'count': len(results),
            'images': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
```

## Error Handling

All functions include comprehensive error handling and will raise exceptions with descriptive messages:

```python
try:
    results = search_images("invalid query that fails")
except Exception as e:
    print(f"Search failed: {e}")

try:
    download_image("invalid-url", "path.jpg")
except Exception as e:
    print(f"Download failed: {e}")
```

## Features

- **Headless Operation**: Selenium configured for headless browser operation suitable for servers
- **Automatic WebDriver Management**: Uses webdriver-manager for automatic ChromeDriver setup
- **Comprehensive Filters**: Support for color, size, type, format, and other search filters
- **Error Handling**: Robust error handling with descriptive messages
- **No CLI Dependencies**: Pure programmatic interface, no command-line arguments required
- **Flask-Ready**: Designed for easy integration with web applications

## Testing

Run the verification script to ensure everything is working:

```bash
python verify_implementation.py
```

Run the example usage:

```bash
python example_usage.py
```

Run the basic tests:

```bash
python test_image_downloader.py
```

## Limitations

- Requires internet connection for Google Images access
- Subject to Google's rate limiting and anti-bot measures
- Large search limits (>100) may take longer due to page scrolling requirements
- Some images may not be downloadable due to source server restrictions
