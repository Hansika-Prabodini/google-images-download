#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Core utilities for batch image downloading.

Provides Result schema, filename utilities, atomic write operations,
and thread-safe HTTP session management.
"""

import os
import re
import threading
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional, Iterable, Dict
from urllib.parse import urlparse, unquote

import requests
from requests.adapters import HTTPAdapter


# Version for User-Agent
__version__ = "2.8.0"


@dataclass
class Result:
    """
    Result schema for download operations.
    
    Fields represent the outcome of a single image download attempt.
    """
    url: str
    status: str  # "ok" | "skipped" | "failed"
    path: Optional[str]
    error: Optional[str]
    bytes: int
    elapsed_ms: int
    from_cache: bool


def to_dict(result: Result) -> Dict:
    """
    Convert Result to dict with deterministic key ordering.
    
    Keys are returned in the exact order:
    ["url", "status", "path", "error", "bytes", "elapsed_ms", "from_cache"]
    
    Args:
        result: Result instance to convert
        
    Returns:
        Ordered dict suitable for JSON serialization
    """
    return {
        "url": result.url,
        "status": result.status,
        "path": result.path,
        "error": result.error,
        "bytes": result.bytes,
        "elapsed_ms": result.elapsed_ms,
        "from_cache": result.from_cache,
    }


def sanitize_filename(name: str) -> str:
    """
    Returns a filesystem-safe filename.
    
    - Replaces path separators with "_"
    - Removes control characters
    - Collapses repeated whitespace to single spaces
    - Trims to 120 chars, preserving extension
    - Avoids Windows reserved names by suffixing "_"
    
    Args:
        name: Original filename
        
    Returns:
        Sanitized filename safe for all filesystems
    """
    if not name:
        return "unnamed"
    
    # Replace path separators with underscore
    sanitized = name.replace("/", "_").replace("\\", "_")
    
    # Remove control characters (ASCII 0-31 and 127)
    sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)
    
    # Remove or replace other problematic characters
    # Keep alphanumeric, spaces, dots, dashes, underscores
    sanitized = re.sub(r'[<>:"|?*]', '', sanitized)
    
    # Collapse multiple spaces to single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Strip leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    
    if not sanitized:
        return "unnamed"
    
    # Split extension
    if '.' in sanitized:
        parts = sanitized.rsplit('.', 1)
        base = parts[0]
        ext = '.' + parts[1]
    else:
        base = sanitized
        ext = ''
    
    # Limit base name length (reserve space for extension)
    max_base_len = 120 - len(ext)
    if len(base) > max_base_len:
        base = base[:max_base_len].rstrip(' .')
    
    sanitized = base + ext
    
    # Check for Windows reserved names
    windows_reserved = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    # Check base name (without extension) against reserved names
    base_upper = base.upper()
    if base_upper in windows_reserved:
        sanitized = base + '_' + ext
    
    return sanitized


def choose_extension(content_type: Optional[str], url_fallback: str) -> str:
    """
    Choose file extension from Content-Type or URL.
    
    Maps image/* content types to normalized extensions.
    Falls back to URL path extraction if content_type is missing.
    Defaults to ".jpg" if unknown.
    
    Args:
        content_type: HTTP Content-Type header value (e.g., "image/jpeg")
        url_fallback: URL to extract extension from if content_type unavailable
        
    Returns:
        Normalized extension with leading dot (e.g., ".jpg", ".png")
    """
    # Known image type mappings
    content_type_map = {
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp',
        'image/bmp': '.bmp',
        'image/x-ms-bmp': '.bmp',
        'image/tiff': '.tif',
        'image/x-tiff': '.tif',
        'image/svg+xml': '.svg',
        'image/x-icon': '.ico',
    }
    
    # Valid image extensions for URL fallback
    valid_extensions = {
        '.jpg', '.jpeg', '.png', '.gif', '.webp', 
        '.bmp', '.tif', '.tiff', '.svg', '.ico'
    }
    
    # Try Content-Type first
    if content_type:
        # Extract base type (remove parameters like charset)
        base_type = content_type.split(';')[0].strip().lower()
        
        if base_type in content_type_map:
            return content_type_map[base_type]
    
    # Fallback to URL extension
    if url_fallback:
        try:
            # Parse URL and get path
            parsed = urlparse(url_fallback)
            path = unquote(parsed.path)
            
            # Extract extension
            if '.' in path:
                ext = '.' + path.rsplit('.', 1)[1].lower()
                # Remove query params if they snuck in
                ext = ext.split('?')[0].split('#')[0]
                
                # Normalize .jpeg to .jpg
                if ext == '.jpeg':
                    ext = '.jpg'
                elif ext == '.tiff':
                    ext = '.tif'
                
                # Validate extension
                if ext in valid_extensions:
                    return ext
        except:
            pass
    
    # Default to .jpg
    return '.jpg'


def ensure_unique_path(dest_dir: str, base_name: str, ext: str) -> Path:
    """
    Ensure non-colliding path by appending numeric suffix when needed.
    
    If the path exists, appends " (n)" before extension, starting at n=1.
    
    Args:
        dest_dir: Destination directory path
        base_name: Base filename (without extension)
        ext: File extension (with leading dot)
        
    Returns:
        Path object guaranteed not to exist
    """
    dest_path = Path(dest_dir)
    
    # Try original name first
    target = dest_path / f"{base_name}{ext}"
    if not target.exists():
        return target
    
    # Append numeric suffix
    counter = 1
    while True:
        target = dest_path / f"{base_name} ({counter}){ext}"
        if not target.exists():
            return target
        counter += 1


def write_temp_then_replace(target_path: Path, stream_iterable: Iterable[bytes]) -> int:
    """
    Atomically write data to target_path via temp file.
    
    Writes to temporary file in same directory, flushes and fsyncs,
    then atomically replaces target. Creates parent directories.
    Cleans up temp file on error.
    
    Args:
        target_path: Final destination path
        stream_iterable: Iterable yielding bytes chunks to write
        
    Returns:
        Total bytes written
        
    Raises:
        Exception: If write or replace fails
    """
    target_path = Path(target_path)
    
    # Create parent directories
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    temp_file = None
    temp_path = None
    total_bytes = 0
    
    try:
        # Create temp file in same directory as target
        temp_file = NamedTemporaryFile(
            mode='wb',
            delete=False,
            dir=target_path.parent,
            prefix=target_path.name + '.tmp-',
            suffix=''
        )
        temp_path = Path(temp_file.name)
        
        # Write all chunks
        for chunk in stream_iterable:
            if chunk:
                temp_file.write(chunk)
                total_bytes += len(chunk)
        
        # Flush and sync to disk
        temp_file.flush()
        os.fsync(temp_file.fileno())
        temp_file.close()
        
        # Atomically replace target
        os.replace(str(temp_path), str(target_path))
        
        return total_bytes
        
    except Exception as e:
        # Clean up temp file on error
        if temp_file:
            try:
                temp_file.close()
            except:
                pass
        
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass
        
        raise Exception(f"Failed to write {target_path}: {str(e)}")


# Thread-local storage for HTTP sessions
_thread_local = threading.local()


def get_session() -> requests.Session:
    """
    Get or create thread-local requests.Session.
    
    Returns the same Session within a thread, creating it on first call.
    Thread-safe via threading.local().
    
    Configures default headers:
    - User-Agent: ImageDownloader/<version> (+https://github.com/hardikvasa/google-images-download)
    - Accept: */*
    - Accept-Encoding: gzip, deflate
    
    Returns:
        requests.Session instance
    """
    if not hasattr(_thread_local, 'session'):
        session = requests.Session()
        
        # Set default headers
        session.headers.update({
            'User-Agent': f'ImageDownloader/{__version__} (+https://github.com/hardikvasa/google-images-download)',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
        })
        
        # Configure HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0  # Retry logic will be in separate module
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        _thread_local.session = session
    
    return _thread_local.session
