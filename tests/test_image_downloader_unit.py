import os
import io
import json
import ssl
from unittest import mock
import builtins

import pytest

import image_downloader as mod


class TestBuildUrlParameters:
    def test_empty_filters_returns_empty_string(self):
        dl = mod.ImageDownloader()
        assert dl._build_url_parameters({}) == ""

    def test_composes_multiple_params(self):
        dl = mod.ImageDownloader()
        filters = {
            'color': 'blue',
            'type': 'photo',
            'size': 'large',
            'format': 'jpg'
        }
        tbs = dl._build_url_parameters(filters)
        # must start with &tbs=
        assert tbs.startswith("&tbs=")
        # contains specific encoded fragments in any order separated by commas
        assert 'ic:specific,isc:blue' in tbs
        assert 'itp:photo' in tbs
        assert 'isz:l' in tbs
        assert 'ift:jpg' in tbs


class TestBuildSearchUrl:
    def test_safe_search_flag(self):
        dl = mod.ImageDownloader()
        params = dl._build_url_parameters({'color': 'red'})
        url = dl._build_search_url('kittens', params, {'safe_search': True})
        assert 'safe=active' in url

    def test_no_safe_search_by_default(self):
        dl = mod.ImageDownloader()
        params = dl._build_url_parameters({'color': 'red'})
        url = dl._build_search_url('kittens', params, None)
        assert 'safe=active' not in url


class TestGetAllItems:
    def make_html_with_items(self, objects):
        # Create a fake HTML chunk that contains JSON objects inside elements with the expected class
        parts = []
        for obj in objects:
            json_str = json.dumps(obj)
            parts.append(f'<div class="rg_meta notranslate">{json_str}</div>')
        return "..." + "".join(parts) + "..."

    def test_parses_multiple_items(self):
        dl = mod.ImageDownloader()
        raw_objs = [
            {"ou": "https://example.com/a.jpg", "tu": "https://thumb/a.jpg", "pt": "A", "ru": "https://host/a", "ow": 640, "oh": 480, "ity": "jpg", "rh": "example.com"},
            {"ou": "https://example.com/b.png", "tu": "https://thumb/b.png", "pt": "B", "ru": "https://host/b", "ow": 800, "oh": 600, "ity": "png", "rh": "example.com"},
        ]
        html = self.make_html_with_items(raw_objs)
        items = dl._get_all_items(html, limit=10)
        assert len(items) == 2
        # verify formatting mapping
        assert items[0]['image_link'] == raw_objs[0]['ou']
        assert items[0]['image_thumbnail_url'] == raw_objs[0]['tu']
        assert items[0]['image_width'] == raw_objs[0]['ow']
        assert items[0]['image_height'] == raw_objs[0]['oh']
        assert items[0]['image_format'] == raw_objs[0]['ity']


class TestSearchImages:
    def test_uses_download_page_when_limit_small(self, monkeypatch):
        dl = mod.ImageDownloader()

        # Prepare fake HTML content for _download_page
        obj = {"ou": "https://example.com/a.jpg", "tu": "t", "pt": "title", "ru": "src", "ow": 1, "oh": 1, "ity": "jpg", "rh": "host"}
        fake_html = f'<div class="rg_meta notranslate">{json.dumps(obj)}</div>'

        def fake_download_page(url):
            return fake_html

        # Patch methods
        monkeypatch.setattr(dl, "_download_page", lambda url: fake_html)
        monkeypatch.setattr(dl, "_get_all_items", lambda page, limit: [dl._format_object(obj)])

        results = dl.search_images("query", limit=5)
        assert len(results) == 1
        assert results[0]['url'] == obj['ou']

    def test_uses_download_extended_when_limit_large(self, monkeypatch):
        dl = mod.ImageDownloader()

        obj = {"ou": "https://example.com/a.jpg", "tu": "t", "pt": "title", "ru": "src", "ow": 1, "oh": 1, "ity": "jpg", "rh": "host"}
        fake_html = f'<div class="rg_meta notranslate">{json.dumps(obj)}</div>'

        monkeypatch.setattr(dl, "_download_extended_page", lambda url, chromedriver_path: fake_html)
        monkeypatch.setattr(dl, "_get_all_items", lambda page, limit: [dl._format_object(obj)])

        results = dl.search_images("query", limit=150)
        assert len(results) == 1
        assert results[0]['url'] == obj['ou']


class TestDownloadImage:
    @mock.patch("image_downloader.urlopen")
    def test_download_image_writes_bytes(self, mock_urlopen, tmp_path):
        # Prepare fake response
        class DummyResp:
            def __init__(self, data=b"abc"):
                self._data = data
            def read(self):
                return self._data
            def close(self):
                pass
        mock_urlopen.return_value = DummyResp(b"xyz")

        dl = mod.ImageDownloader()
        dest = tmp_path / "out" / "file.jpg"
        out_path = dl.download_image("https://example.com/img.jpg", str(dest))
        assert os.path.exists(out_path)
        with open(out_path, 'rb') as f:
            assert f.read() == b"xyz"
