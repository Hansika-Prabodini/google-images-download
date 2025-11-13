#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comprehensive unit tests for utils.download_core module.

Tests Result schema, filename utilities, atomic write operations,
and thread-safe HTTP session management.
"""

import os
import sys
import unittest
import threading
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.download_core import (
    Result,
    to_dict,
    sanitize_filename,
    choose_extension,
    ensure_unique_path,
    write_temp_then_replace,
    get_session,
)


class TestResult(unittest.TestCase):
    """Test Result dataclass."""
    
    def test_result_creation(self):
        """Test Result can be created with all fields."""
        result = Result(
            url="https://example.com/image.jpg",
            status="ok",
            path="/path/to/image.jpg",
            error=None,
            bytes=1024,
            elapsed_ms=150,
            from_cache=False
        )
        
        self.assertEqual(result.url, "https://example.com/image.jpg")
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.path, "/path/to/image.jpg")
        self.assertIsNone(result.error)
        self.assertEqual(result.bytes, 1024)
        self.assertEqual(result.elapsed_ms, 150)
        self.assertFalse(result.from_cache)
    
    def test_result_with_error(self):
        """Test Result with error status."""
        result = Result(
            url="https://example.com/fail.jpg",
            status="failed",
            path=None,
            error="Connection timeout",
            bytes=0,
            elapsed_ms=5000,
            from_cache=False
        )
        
        self.assertEqual(result.status, "failed")
        self.assertIsNone(result.path)
        self.assertEqual(result.error, "Connection timeout")
        self.assertEqual(result.bytes, 0)


class TestToDict(unittest.TestCase):
    """Test to_dict function."""
    
    def test_to_dict_ordering(self):
        """Test that to_dict returns keys in exact specified order."""
        result = Result(
            url="https://example.com/test.jpg",
            status="ok",
            path="/tmp/test.jpg",
            error=None,
            bytes=2048,
            elapsed_ms=200,
            from_cache=True
        )
        
        d = to_dict(result)
        
        # Check exact key ordering
        keys = list(d.keys())
        expected_keys = ["url", "status", "path", "error", "bytes", "elapsed_ms", "from_cache"]
        self.assertEqual(keys, expected_keys)
    
    def test_to_dict_types(self):
        """Test that to_dict returns stable types suitable for JSON."""
        result = Result(
            url="https://example.com/test.jpg",
            status="ok",
            path="/tmp/test.jpg",
            error=None,
            bytes=2048,
            elapsed_ms=200,
            from_cache=True
        )
        
        d = to_dict(result)
        
        self.assertIsInstance(d["url"], str)
        self.assertIsInstance(d["status"], str)
        self.assertIsInstance(d["path"], str)
        self.assertIsNone(d["error"])
        self.assertIsInstance(d["bytes"], int)
        self.assertIsInstance(d["elapsed_ms"], int)
        self.assertIsInstance(d["from_cache"], bool)
    
    def test_to_dict_with_nulls(self):
        """Test to_dict with None values."""
        result = Result(
            url="https://example.com/skipped.jpg",
            status="skipped",
            path=None,
            error=None,
            bytes=0,
            elapsed_ms=0,
            from_cache=False
        )
        
        d = to_dict(result)
        
        self.assertIsNone(d["path"])
        self.assertIsNone(d["error"])


class TestSanitizeFilename(unittest.TestCase):
    """Test sanitize_filename function."""
    
    def test_simple_filename(self):
        """Test simple valid filename."""
        result = sanitize_filename("image.jpg")
        self.assertEqual(result, "image.jpg")
    
    def test_path_separators(self):
        """Test that path separators are replaced."""
        result = sanitize_filename("path/to/file.jpg")
        self.assertEqual(result, "path_to_file.jpg")
        
        result = sanitize_filename("path\\to\\file.jpg")
        self.assertEqual(result, "path_to_file.jpg")
    
    def test_control_characters(self):
        """Test that control characters are removed."""
        result = sanitize_filename("file\x00\x1f\x7fname.jpg")
        self.assertEqual(result, "filename.jpg")
    
    def test_problematic_characters(self):
        """Test removal of problematic characters."""
        result = sanitize_filename('file<>:"|?*name.jpg')
        self.assertEqual(result, "filename.jpg")
    
    def test_multiple_spaces(self):
        """Test that multiple spaces are collapsed."""
        result = sanitize_filename("file    name   test.jpg")
        self.assertEqual(result, "file name test.jpg")
    
    def test_whitespace_trimming(self):
        """Test that leading/trailing whitespace is trimmed."""
        result = sanitize_filename("  filename.jpg  ")
        self.assertEqual(result, "filename.jpg")
        
        result = sanitize_filename("...filename.jpg...")
        self.assertEqual(result, "filename.jpg")
    
    def test_long_filename(self):
        """Test that long filenames are trimmed to 120 chars."""
        long_name = "a" * 150 + ".jpg"
        result = sanitize_filename(long_name)
        self.assertLessEqual(len(result), 120)
        self.assertTrue(result.endswith(".jpg"))
    
    def test_long_filename_preserves_extension(self):
        """Test that extension is preserved when trimming."""
        long_base = "x" * 150
        name = f"{long_base}.longextension"
        result = sanitize_filename(name)
        self.assertTrue(result.endswith(".longextension"))
        self.assertLessEqual(len(result), 120)
    
    def test_windows_reserved_names(self):
        """Test that Windows reserved names are suffixed."""
        reserved = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]
        
        for name in reserved:
            result = sanitize_filename(f"{name}.jpg")
            self.assertEqual(result, f"{name}_.jpg")
            
            # Test lowercase versions
            result = sanitize_filename(f"{name.lower()}.jpg")
            self.assertEqual(result, f"{name.lower()}_.jpg")
    
    def test_empty_filename(self):
        """Test empty filename returns default."""
        result = sanitize_filename("")
        self.assertEqual(result, "unnamed")
    
    def test_all_invalid_chars(self):
        """Test filename with all invalid characters."""
        result = sanitize_filename("///...")
        self.assertEqual(result, "unnamed")
    
    def test_no_extension(self):
        """Test filename without extension."""
        result = sanitize_filename("filename")
        self.assertEqual(result, "filename")
    
    def test_stability(self):
        """Test that function is stable across calls."""
        name = "test file (1).jpg"
        result1 = sanitize_filename(name)
        result2 = sanitize_filename(name)
        self.assertEqual(result1, result2)


class TestChooseExtension(unittest.TestCase):
    """Test choose_extension function."""
    
    def test_content_type_jpeg(self):
        """Test mapping of image/jpeg."""
        result = choose_extension("image/jpeg", "http://example.com/test")
        self.assertEqual(result, ".jpg")
    
    def test_content_type_png(self):
        """Test mapping of image/png."""
        result = choose_extension("image/png", "http://example.com/test")
        self.assertEqual(result, ".png")
    
    def test_content_type_gif(self):
        """Test mapping of image/gif."""
        result = choose_extension("image/gif", "http://example.com/test")
        self.assertEqual(result, ".gif")
    
    def test_content_type_webp(self):
        """Test mapping of image/webp."""
        result = choose_extension("image/webp", "http://example.com/test")
        self.assertEqual(result, ".webp")
    
    def test_content_type_bmp(self):
        """Test mapping of image/bmp."""
        result = choose_extension("image/bmp", "http://example.com/test")
        self.assertEqual(result, ".bmp")
    
    def test_content_type_tiff(self):
        """Test mapping of image/tiff."""
        result = choose_extension("image/tiff", "http://example.com/test")
        self.assertEqual(result, ".tif")
    
    def test_content_type_with_parameters(self):
        """Test content-type with parameters like charset."""
        result = choose_extension("image/jpeg; charset=utf-8", "http://example.com/test")
        self.assertEqual(result, ".jpg")
    
    def test_non_image_content_type(self):
        """Test non-image content-type falls back to URL."""
        result = choose_extension("text/html", "http://example.com/image.png")
        self.assertEqual(result, ".png")
    
    def test_url_fallback_jpg(self):
        """Test URL fallback for .jpg."""
        result = choose_extension(None, "http://example.com/photo.jpg")
        self.assertEqual(result, ".jpg")
    
    def test_url_fallback_png(self):
        """Test URL fallback for .png."""
        result = choose_extension(None, "http://example.com/image.png")
        self.assertEqual(result, ".png")
    
    def test_url_with_query_params(self):
        """Test URL with query parameters."""
        result = choose_extension(None, "http://example.com/image.jpg?size=large")
        self.assertEqual(result, ".jpg")
    
    def test_jpeg_normalized_to_jpg(self):
        """Test that .jpeg is normalized to .jpg."""
        result = choose_extension(None, "http://example.com/photo.jpeg")
        self.assertEqual(result, ".jpg")
    
    def test_tiff_normalized_to_tif(self):
        """Test that .tiff is normalized to .tif."""
        result = choose_extension(None, "http://example.com/scan.tiff")
        self.assertEqual(result, ".tif")
    
    def test_unknown_extension_defaults_jpg(self):
        """Test unknown extension defaults to .jpg."""
        result = choose_extension(None, "http://example.com/file.unknown")
        self.assertEqual(result, ".jpg")
    
    def test_no_extension_defaults_jpg(self):
        """Test no extension defaults to .jpg."""
        result = choose_extension(None, "http://example.com/file")
        self.assertEqual(result, ".jpg")
    
    def test_case_insensitive(self):
        """Test that extensions are lowercased."""
        result = choose_extension(None, "http://example.com/IMAGE.PNG")
        self.assertEqual(result, ".png")
    
    def test_malformed_url(self):
        """Test malformed URL defaults to .jpg."""
        result = choose_extension(None, "not a url")
        self.assertEqual(result, ".jpg")


class TestEnsureUniquePath(unittest.TestCase):
    """Test ensure_unique_path function."""
    
    def setUp(self):
        """Create temp directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_non_existing_path(self):
        """Test that non-existing path is returned as-is."""
        result = ensure_unique_path(self.temp_dir, "test", ".jpg")
        expected = Path(self.temp_dir) / "test.jpg"
        self.assertEqual(result, expected)
    
    def test_existing_path_appends_suffix(self):
        """Test that existing path gets numeric suffix."""
        # Create existing file
        existing = Path(self.temp_dir) / "test.jpg"
        existing.touch()
        
        result = ensure_unique_path(self.temp_dir, "test", ".jpg")
        expected = Path(self.temp_dir) / "test (1).jpg"
        self.assertEqual(result, expected)
    
    def test_multiple_existing_paths(self):
        """Test incrementing suffix for multiple collisions."""
        # Create multiple existing files
        (Path(self.temp_dir) / "test.jpg").touch()
        (Path(self.temp_dir) / "test (1).jpg").touch()
        (Path(self.temp_dir) / "test (2).jpg").touch()
        
        result = ensure_unique_path(self.temp_dir, "test", ".jpg")
        expected = Path(self.temp_dir) / "test (3).jpg"
        self.assertEqual(result, expected)
    
    def test_returns_path_object(self):
        """Test that return value is a Path object."""
        result = ensure_unique_path(self.temp_dir, "test", ".jpg")
        self.assertIsInstance(result, Path)
    
    def test_different_extensions(self):
        """Test with different file extensions."""
        result = ensure_unique_path(self.temp_dir, "image", ".png")
        expected = Path(self.temp_dir) / "image.png"
        self.assertEqual(result, expected)


class TestWriteTempThenReplace(unittest.TestCase):
    """Test write_temp_then_replace function."""
    
    def setUp(self):
        """Create temp directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_successful_write(self):
        """Test successful atomic write."""
        target = Path(self.temp_dir) / "test.jpg"
        data = [b"chunk1", b"chunk2", b"chunk3"]
        
        bytes_written = write_temp_then_replace(target, data)
        
        # Check file exists and has correct content
        self.assertTrue(target.exists())
        self.assertEqual(target.read_bytes(), b"chunk1chunk2chunk3")
        self.assertEqual(bytes_written, 18)
    
    def test_creates_parent_directories(self):
        """Test that parent directories are created."""
        target = Path(self.temp_dir) / "subdir" / "nested" / "test.jpg"
        data = [b"test"]
        
        bytes_written = write_temp_then_replace(target, data)
        
        self.assertTrue(target.exists())
        self.assertEqual(bytes_written, 4)
    
    def test_empty_chunks_skipped(self):
        """Test that empty chunks are skipped."""
        target = Path(self.temp_dir) / "test.jpg"
        data = [b"data", b"", b"more"]
        
        bytes_written = write_temp_then_replace(target, data)
        
        self.assertEqual(target.read_bytes(), b"datamore")
        self.assertEqual(bytes_written, 8)
    
    def test_replaces_existing_file(self):
        """Test that existing file is replaced atomically."""
        target = Path(self.temp_dir) / "test.jpg"
        target.write_bytes(b"old content")
        
        data = [b"new content"]
        bytes_written = write_temp_then_replace(target, data)
        
        self.assertEqual(target.read_bytes(), b"new content")
        self.assertEqual(bytes_written, 11)
    
    def test_cleanup_on_error(self):
        """Test that temp file is cleaned up on error."""
        target = Path(self.temp_dir) / "test.jpg"
        
        # Create a failing iterable
        def failing_generator():
            yield b"some data"
            raise RuntimeError("Simulated failure")
        
        with self.assertRaises(Exception):
            write_temp_then_replace(target, failing_generator())
        
        # Target should not exist
        self.assertFalse(target.exists())
        
        # No temp files should be left behind
        temp_files = list(Path(self.temp_dir).glob("*.tmp-*"))
        self.assertEqual(len(temp_files), 0)
    
    def test_returns_byte_count(self):
        """Test that correct byte count is returned."""
        target = Path(self.temp_dir) / "test.jpg"
        data = [b"x" * 100, b"y" * 200, b"z" * 300]
        
        bytes_written = write_temp_then_replace(target, data)
        
        self.assertEqual(bytes_written, 600)


class TestGetSession(unittest.TestCase):
    """Test get_session function."""
    
    def test_returns_requests_session(self):
        """Test that get_session returns a requests.Session."""
        session = get_session()
        self.assertIsInstance(session, __import__('requests').Session)
    
    def test_same_session_in_thread(self):
        """Test that same session is returned within thread."""
        session1 = get_session()
        session2 = get_session()
        self.assertIs(session1, session2)
    
    def test_different_sessions_across_threads(self):
        """Test that different sessions are used in different threads."""
        sessions = []
        
        def get_session_in_thread():
            sessions.append(get_session())
        
        thread1 = threading.Thread(target=get_session_in_thread)
        thread2 = threading.Thread(target=get_session_in_thread)
        
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        
        self.assertEqual(len(sessions), 2)
        self.assertIsNot(sessions[0], sessions[1])
    
    def test_user_agent_header(self):
        """Test that User-Agent header is set."""
        session = get_session()
        user_agent = session.headers.get('User-Agent')
        
        self.assertIsNotNone(user_agent)
        self.assertIn('ImageDownloader', user_agent)
        self.assertIn('github.com', user_agent)
    
    def test_accept_header(self):
        """Test that Accept header is set."""
        session = get_session()
        accept = session.headers.get('Accept')
        
        self.assertEqual(accept, '*/*')
    
    def test_accept_encoding_header(self):
        """Test that Accept-Encoding header is set."""
        session = get_session()
        encoding = session.headers.get('Accept-Encoding')
        
        self.assertIn('gzip', encoding)
        self.assertIn('deflate', encoding)
    
    def test_ssl_verify_enabled(self):
        """Test that SSL verification is enabled by default."""
        session = get_session()
        # requests.Session.verify defaults to True
        self.assertTrue(session.verify)


if __name__ == '__main__':
    unittest.main()
