Tests README

This document explains the purpose of tests/test_bug.py and how to run it.

What is tested
- Regression test for URL parameter construction when filtering by color "teal".
- Ensures _build_url_parameters maps the color correctly to "ic:specific,isc:teal" and not the previous typo "isc:teel".

Why this exists
- A prior bug had a misspelling in the color mapping for teal ("teel").
- The test catches regressions if that typo reappears or mapping changes incorrectly.

How to run
- From project root, run:
  - With pytest: `pytest -q tests/test_bug.py`
  - Or run full suite: `pytest -q`

Expected behavior
- The test asserts that the built params contain "ic:specific,isc:teal" and do not contain "isc:teel".
- If the implementation is correct, the test passes.

Related code
- Implementation lives in image_downloader.py, method ImageDownloader._build_url_parameters.

Troubleshooting
- If the test fails expecting teal mapping, open image_downloader.py and check the color mapping dict in _build_url_parameters.
- Ensure no extra spaces or case mismatch; keys are lowercase.

License/Attribution
- This project adapts logic from google_images_download; see top-level README and Licence.txt for details.
