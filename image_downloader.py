#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Image Downloader Module

Provides programmatic interface for searching and downloading images from Google Images.
Extracted and adapted from google_images_download for use in web applications.
"""

import sys
import os
import time
import json
import re
import ssl
import socket
import copy
import random
from typing import List, Dict, Optional, Tuple

# Import libraries based on Python version
version = (3, 0)
cur_version = sys.version_info
if cur_version >= version:  # Python 3.0+
    import urllib.request
    from urllib.request import Request, urlopen
    from urllib.request import URLError, HTTPError
    from urllib.parse import quote
    import http.client
    from http.client import IncompleteRead, BadStatusLine
    http.client._MAXHEADERS = 1000
else:  # Python 2.x
    import urllib2
    from urllib2 import Request, urlopen
    from urllib2 import URLError, HTTPError
    from urllib import quote
    import httplib
    from httplib import IncompleteRead, BadStatusLine
    httplib._MAXHEADERS = 1000


class ImageDownloader:
    """Main class for image search and download functionality."""

    # Recognized per-call override keys
    _RECOGNIZED_OVERRIDE_KEYS = {
        'max_retries', 'backoff_base', 'backoff_jitter', 'rate_limit_rps',
        'user_agents', 'proxies', 'timeout'
    }

    # Default User-Agents used when not overridden
    _DEFAULT_PAGE_UA = (
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/41.0.2228.0 Safari/537.36"
    )
    _DEFAULT_IMAGE_UA = (
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) "
        "Chrome/24.0.1312.27 Safari/537.17"
    )

    def __init__(self, chromedriver_path: Optional[str] = None):
        """
        Initialize the ImageDownloader.

        Args:
            chromedriver_path: Path to chromedriver executable. If None, will try to auto-detect.
        """
        self.chromedriver_path = chromedriver_path
        # Instance-level defaults for reliability-related settings. These are
        # intentionally conservative and can be overridden per call via options.
        self._config: Dict[str, Optional[object]] = {
            'max_retries': 0,
            'backoff_base': 0.5,
            'backoff_jitter': 0.1,
            'rate_limit_rps': None,
            'user_agents': None,  # When None, use legacy per-call defaults to preserve behavior
            'proxies': None,
            'timeout': None,      # When None, use function parameter defaults
        }

    def search_images(self, query: str, limit: int = 10, filters: Optional[Dict] = None,
                      chromedriver_path: Optional[str] = None, options: Optional[Dict] = None) -> List[Dict]:
        """
        Search for images and return metadata without downloading.

        Args:
            query: Search term/query
            limit: Number of images to find (default: 10, max recommended: 100 for reliability)
            filters: Optional dict containing search filters like:
                - 'color': str (red, orange, yellow, green, teal, blue, purple, pink, white, gray, black, brown)
                - 'color_type': str (full-color, black-and-white, transparent)
                - 'size': str (large, medium, icon, >400*300, etc.)
                - 'type': str (face, photo, clipart, line-drawing, animated)
                - 'format': str (jpg, gif, png, bmp, svg, webp, ico)
                - 'time': str (past-24-hours, past-7-days, past-month, past-year)
                - 'usage_rights': str (labeled-for-reuse-with-modifications, etc.)
                - 'safe_search': bool
            chromedriver_path: Optional path to chromedriver to override the instance default for this call.
            options: Optional dict of per-call overrides for reliability settings. Recognized keys:
                - max_retries, backoff_base, backoff_jitter, rate_limit_rps, user_agents, proxies, timeout
                Precedence: per-call options override instance-level defaults for this call only.

        Returns:
            List of dicts with image metadata. Each dict contains:
                - 'url': str (direct image URL)
                - 'thumbnail_url': str (thumbnail URL)
                - 'title': str (image description/title)
                - 'source': str (source website URL)
                - 'width': int (image width in pixels)
                - 'height': int (image height in pixels)
                - 'format': str (image format like jpg, png, etc.)

        Raises:
            Exception: If search fails or no images found
        """
        try:
            # Prepare search parameters
            params = self._build_url_parameters(filters or {})
            search_url = self._build_search_url(query, params, filters)

            effective = self._merge_effective_options(options)

            # Download page content
            driver_path = chromedriver_path if chromedriver_path is not None else self.chromedriver_path
            if limit <= 100:
                raw_html = self._download_page(search_url, effective)
            else:
                raw_html = self._download_extended_page(search_url, driver_path, effective)

            # Extract image metadata
            items = self._get_all_items(raw_html, limit)

            # Format results
            results = []
            for item in items:
                if item:  # Skip empty items
                    result = {
                        'url': item.get('image_link', ''),
                        'thumbnail_url': item.get('image_thumbnail_url', ''),
                        'title': item.get('image_description', ''),
                        'source': item.get('image_source', ''),
                        'width': item.get('image_width', 0),
                        'height': item.get('image_height', 0),
                        'format': item.get('image_format', ''),
                        'host': item.get('image_host', '')
                    }
                    results.append(result)

            if not results:
                raise Exception(f"No images found for query: {query}")

            return results

        except Exception as e:
            raise Exception(f"Search failed for query '{query}': {str(e)}")

    def download_image(self, image_url: str, destination_path: str, timeout: int = 10,
                       options: Optional[Dict] = None) -> str:
        """
        Download a single image from URL to specified path.

        Args:
            image_url: Direct URL to the image
            destination_path: Local file path where image should be saved
            timeout: Download timeout in seconds (default: 10). If options includes 'timeout',
                     options['timeout'] takes precedence for this call.
            options: Optional dict of per-call overrides: max_retries, backoff_base, backoff_jitter,
                     rate_limit_rps, user_agents, proxies, timeout.

        Returns:
            str: Path to the downloaded file

        Raises:
            Exception: If download fails
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(destination_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            effective = self._merge_effective_options(options, per_call_timeout=timeout)

            # Perform HTTP GET with reliability features
            data = self._http_get_bytes(
                url=image_url,
                effective=effective,
                default_user_agent=self._DEFAULT_IMAGE_UA,
            )

            # Save to file
            with open(destination_path, 'wb') as output_file:
                output_file.write(data)

            return destination_path

        except HTTPError as e:
            raise Exception(f"HTTP error downloading image: {e}")
        except URLError as e:
            raise Exception(f"URL error downloading image: {e}")
        except IOError as e:
            raise Exception(f"IO error saving image: {e}")
        except Exception as e:
            raise Exception(f"Failed to download image from {image_url}: {str(e)}")

    # Internal helper methods (adapted from original code)

    def _validate_options(self, options: Optional[Dict]) -> None:
        if not options:
            return
        unknown = set(options.keys()) - self._RECOGNIZED_OVERRIDE_KEYS
        if unknown:
            raise ValueError(f"Unsupported options: {sorted(list(unknown))}")

    def _merge_effective_options(self, options: Optional[Dict], per_call_timeout: Optional[float] = None) -> Dict:
        """Merge instance defaults, per-parameter values and per-call options.

        Precedence:
        - Instance defaults (self._config)
        - Dedicated parameter (per_call_timeout)
        - Per-call options (options["timeout"]) takes final precedence over timeout
        """
        self._validate_options(options)
        # Start with instance defaults (copy to avoid mutation)
        eff = {
            'max_retries': self._config.get('max_retries', 0),
            'backoff_base': self._config.get('backoff_base', 0.5),
            'backoff_jitter': self._config.get('backoff_jitter', 0.1),
            'rate_limit_rps': self._config.get('rate_limit_rps', None),
            'user_agents': copy.deepcopy(self._config.get('user_agents', None)),
            'proxies': copy.deepcopy(self._config.get('proxies', None)),
            'timeout': self._config.get('timeout', None),
        }

        # Apply dedicated param
        if per_call_timeout is not None:
            eff['timeout'] = per_call_timeout

        # Apply per-call overrides
        if options:
            for k, v in options.items():
                if v is None:
                    continue  # None means no override
                if k in ('user_agents',):
                    # Copy to avoid sharing
                    if isinstance(v, (list, tuple)):
                        eff[k] = list(v)
                    else:
                        eff[k] = v  # Allow single string
                elif k == 'proxies':
                    if isinstance(v, dict):
                        eff[k] = dict(v)
                    else:
                        eff[k] = v
                else:
                    eff[k] = v

        return eff

    def _select_user_agent(self, effective: Dict, default_user_agent: str) -> str:
        uas = effective.get('user_agents')
        if not uas:
            return default_user_agent
        if isinstance(uas, (list, tuple)) and len(uas) > 0:
            return uas[0]
        if isinstance(uas, str):
            return uas
        return default_user_agent

    def _http_get_bytes(self, url: str, effective: Dict, default_user_agent: str) -> bytes:
        """Perform an HTTP GET returning response bytes with retries/backoff and optional proxies and headers."""
        headers = {
            'User-Agent': self._select_user_agent(effective, default_user_agent)
        }

        # Rate limiting (per call, coarse)
        rps = effective.get('rate_limit_rps')
        if rps and rps > 0:
            min_interval = 1.0 / float(rps)
            time.sleep(min_interval)

        max_retries = int(effective.get('max_retries') or 0)
        backoff_base = float(effective.get('backoff_base') or 0.0)
        backoff_jitter = float(effective.get('backoff_jitter') or 0.0)
        timeout = effective.get('timeout', None)

        # Prepare opener with optional proxies
        proxies = effective.get('proxies')
        proxy_dict = None
        if proxies:
            if isinstance(proxies, str):
                proxy_dict = {'http': proxies, 'https': proxies}
            elif isinstance(proxies, dict):
                proxy_dict = dict(proxies)

        attempt = 0
        last_err = None
        while attempt <= max_retries:
            try:
                req = Request(url, headers=headers)
                ssl_context = ssl.create_default_context()
                if proxy_dict:
                    opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxy_dict))
                    # Note: opener.open does not accept an SSL context parameter; use default context.
                    resp = opener.open(req, timeout=timeout)
                else:
                    resp = urlopen(req, context=ssl_context, timeout=timeout)
                data = resp.read()
                resp.close()
                return data
            except (HTTPError, URLError, socket.timeout, ssl.SSLError, IncompleteRead, BadStatusLine) as e:
                last_err = e
                attempt += 1
                if attempt > max_retries:
                    break
                # Exponential backoff with jitter
                sleep_for = (backoff_base * (2 ** (attempt - 1))) + (random.uniform(0, backoff_jitter) if backoff_jitter else 0)
                if sleep_for > 0:
                    time.sleep(sleep_for)
            except Exception as e:
                last_err = e
                attempt += 1
                if attempt > max_retries:
                    break
                sleep_for = (backoff_base * (2 ** (attempt - 1))) + (random.uniform(0, backoff_jitter) if backoff_jitter else 0)
                if sleep_for > 0:
                    time.sleep(sleep_for)
        # If we reach here, all attempts failed
        if last_err:
            raise last_err
        raise Exception("Request failed")

    def _download_page(self, url: str, effective: Dict) -> str:
        """Download web page content with per-call overrides applied."""
        try:
            data = self._http_get_bytes(url, effective, default_user_agent=self._DEFAULT_PAGE_UA)
            return str(data)
        except Exception as e:
            raise Exception(f"Could not download page {url}: {str(e)}")

    def _download_extended_page(self, url: str, chromedriver_path: Optional[str], effective: Dict) -> str:
        """Download page content using Selenium for >100 images, applying UA/proxy/timeout overrides."""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options

            # Configure Chrome options for headless operation
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1024,768')

            # Apply per-call overrides: user agent and proxy
            ua = self._select_user_agent(effective, default_user_agent=self._DEFAULT_PAGE_UA)
            if ua:
                chrome_options.add_argument(f'--user-agent={ua}')
            proxies = effective.get('proxies')
            if proxies:
                proxy_val = None
                if isinstance(proxies, str):
                    proxy_val = proxies
                elif isinstance(proxies, dict):
                    proxy_val = proxies.get('https') or proxies.get('http')
                if proxy_val:
                    chrome_options.add_argument(f'--proxy-server={proxy_val}')

            # Initialize driver
            if chromedriver_path:
                service = Service(executable_path=chromedriver_path)
                browser = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Try to use webdriver_manager to auto-download chromedriver
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    browser = webdriver.Chrome(service=service, options=chrome_options)
                except ImportError:
                    # Fallback to system chromedriver
                    browser = webdriver.Chrome(options=chrome_options)

            # Apply page load timeout if provided
            if effective.get('timeout') is not None:
                try:
                    browser.set_page_load_timeout(effective['timeout'])
                except Exception:
                    pass

            # Navigate and scroll to load images
            browser.get(url)
            time.sleep(1)

            element = browser.find_element("tag name", "body")

            # Scroll to load more images
            for i in range(30):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)

            # Try to click "Show more results" button
            try:
                show_more_button = browser.find_element("id", "smb")
                show_more_button.click()
                for i in range(50):
                    element.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.3)
            except Exception:
                # Continue scrolling if button not found
                for i in range(10):
                    element.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.3)

            # Get page source and close browser
            source = browser.page_source
            browser.quit()

            return source

        except Exception as e:
            raise Exception(f"Failed to download extended page: {str(e)}")

    def _build_url_parameters(self, filters: Dict) -> str:
        """Build URL parameters from filters."""
        if not filters:
            return ""

        built_url = "&tbs="
        counter = 0

        # Parameter mappings
        params = {
            'color': [filters.get('color'), {
                'red': 'ic:specific,isc:red', 'orange': 'ic:specific,isc:orange',
                'yellow': 'ic:specific,isc:yellow', 'green': 'ic:specific,isc:green',
                'teal': 'ic:specific,isc:teal', 'blue': 'ic:specific,isc:blue',
                'purple': 'ic:specific,isc:purple', 'pink': 'ic:specific,isc:pink',
                'white': 'ic:specific,isc:white', 'gray': 'ic:specific,isc:gray',
                'black': 'ic:specific,isc:black', 'brown': 'ic:specific,isc:brown'
            }],
            'color_type': [filters.get('color_type'), {
                'full-color': 'ic:color', 'black-and-white': 'ic:gray', 'transparent': 'ic:trans'
            }],
            'size': [filters.get('size'), {
                'large': 'isz:l', 'medium': 'isz:m', 'icon': 'isz:i',
                '>400*300': 'isz:lt,islt:qsvga', '>640*480': 'isz:lt,islt:vga',
                '>800*600': 'isz:lt,islt:svga', '>1024*768': 'isz:lt,islt:xga',
                '>2MP': 'isz:lt,islt:2mp', '>4MP': 'isz:lt,islt:4mp',
                '>6MP': 'isz:lt,islt:6mp', '>8MP': 'isz:lt,islt:8mp',
                '>10MP': 'isz:lt,islt:10mp', '>12MP': 'isz:lt:islt:12mp' if False else 'isz:lt,islt:12mp',
                '>15MP': 'isz:lt,islt:15mp', '>20MP': 'isz:lt,islt:20mp',
                '>40MP': 'isz:lt,islt:40mp', '>70MP': 'isz:lt,islt:70mp'
            }],
            'type': [filters.get('type'), {
                'face': 'itp:face', 'photo': 'itp:photo', 'clipart': 'itp:clipart',
                'line-drawing': 'itp:lineart', 'animated': 'itp:animated'
            }],
            'time': [filters.get('time'), {
                'past-24-hours': 'qdr:d', 'past-7-days': 'qdr:w',
                'past-month': 'qdr:m', 'past-year': 'qdr:y'
            }],
            'format': [filters.get('format'), {
                'jpg': 'ift:jpg', 'gif': 'ift:gif', 'png': 'ift:png',
                'bmp': 'ift:bmp', 'svg': 'ift:svg', 'webp': 'webp', 'ico': 'ift:ico'
            }]
        }

        for key, value in params.items():
            if value[0] is not None and value[0] in value[1]:
                ext_param = value[1][value[0]]
                if counter == 0:
                    built_url = built_url + ext_param
                    counter += 1
                else:
                    built_url = built_url + ',' + ext_param
                    counter += 1

        return built_url if counter > 0 else ""

    def _build_search_url(self, search_term: str, params: str, filters: Optional[Dict]) -> str:
        """Build the main search URL."""
        base_url = 'https://www.google.com/search?q=' + quote(search_term.encode('utf-8'))
        url = base_url + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch' + params + '&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'

        # Add safe search if enabled
        if filters and filters.get('safe_search'):
            url += "&safe=active"

        return url

    def _get_all_items(self, page: str, limit: int) -> List[Dict]:
        """Extract image metadata from page HTML."""
        items = []
        count = 0

        while count < limit:
            item, end_content = self._get_next_item(page)
            if item == "no_links" or not item:
                break

            # Format the item for readability
            if isinstance(item, dict):
                formatted_item = self._format_object(item)
                items.append(formatted_item)
                count += 1

            page = page[end_content:] if end_content > 0 else ""
            if not page:
                break

        return items

    def _get_next_item(self, page: str) -> Tuple:
        """Extract next image metadata from HTML."""
        start_line = page.find('rg_meta notranslate')
        if start_line == -1:
            return "no_links", 0

        try:
            start_line = page.find('class="rg_meta notranslate">')
            start_object = page.find('{', start_line + 1)
            end_object = page.find('</div>', start_object + 1)
            object_raw = str(page[start_object:end_object])

            # Parse JSON object
            try:
                object_decode = bytes(object_raw, "utf-8").decode("unicode_escape")
                final_object = json.loads(object_decode)
            except Exception:
                final_object = {}

            return final_object, end_object

        except Exception:
            return {}, page.find('</div>', start_line + 1) if start_line >= 0 else 0

    def _format_object(self, obj: Dict) -> Dict:
        """Format raw image object into standardized structure."""
        return {
            'image_format': obj.get('ity', ''),
            'image_height': obj.get('oh', 0),
            'image_width': obj.get('ow', 0),
            'image_link': obj.get('ou', ''),
            'image_description': obj.get('pt', ''),
            'image_host': obj.get('rh', ''),
            'image_source': obj.get('ru', ''),
            'image_thumbnail_url': obj.get('tu', '')
        }


# Convenience functions for easier usage

def search_images(query: str, limit: int = 10, filters: Optional[Dict] = None, chromedriver_path: Optional[str] = None, options: Optional[Dict] = None) -> List[Dict]:
    """
    Convenience function to search for images.

    Args:
        query: Search term
        limit: Number of images to find (default: 10)
        filters: Optional search filters dict
        chromedriver_path: Path to chromedriver executable
        options: Optional per-call overrides dict with keys: max_retries, backoff_base, backoff_jitter,
                 rate_limit_rps, user_agents, proxies, timeout. Per-call options override instance defaults
                 for that call only.

    Returns:
        List of image metadata dicts
    """
    downloader = ImageDownloader(chromedriver_path)
    return downloader.search_images(query, limit, filters, chromedriver_path=chromedriver_path, options=options)


def download_image(image_url: str, destination_path: str, timeout: int = 10, options: Optional[Dict] = None) -> str:
    """
    Convenience function to download a single image.

    Args:
        image_url: Direct URL to the image
        destination_path: Local path where image should be saved
        timeout: Download timeout in seconds
        options: Optional per-call overrides dict with keys: max_retries, backoff_base, backoff_jitter,
                 rate_limit_rps, user_agents, proxies, timeout. If options includes 'timeout', it takes
                 precedence over the timeout parameter for this call only.

    Returns:
        str: Path to the downloaded file
    """
    downloader = ImageDownloader()
    return downloader.download_image(image_url, destination_path, timeout, options=options)
