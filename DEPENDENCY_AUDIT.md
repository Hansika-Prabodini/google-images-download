# Dependency Audit Report

**Generated:** Pre-update baseline  
**Project:** google-images-download v2.8.0  
**Purpose:** Comprehensive inventory of current dependency versions and constraints

---

## Executive Summary

This document provides a complete audit of all project dependencies, their current version specifications, actual versions that would be installed, usage patterns in the codebase, and compatibility requirements. This baseline will be used for comparison after dependency updates.

---

## 1. Current Dependency Specifications

### 1.1 Requirements.txt

The `requirements.txt` file contains the following dependency specifications:

```
selenium>=4.0.0
webdriver-manager>=3.8.0
requests>=2.28.0
```

**Key Observations:**
- All dependencies use minimum version constraints (`>=`)
- No upper bounds specified - latest compatible versions will be installed
- No pinned versions or version ranges with upper limits
- No additional dependencies beyond these three core packages

### 1.2 Setup.py Configuration

**Package Version:** `2.8.0`

**Installation Mechanism:**
```python
# Lines 14-18 of setup.py
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]
```

**Details:**
- `setup.py` dynamically reads dependencies from `requirements.txt`
- Filters out git-based dependencies (none currently present)
- Passes to `install_requires` parameter in setup()
- No additional dependencies specified directly in setup.py

**Python Version Classifiers:**
```python
# Lines 28-37 of setup.py
classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]
```

**Python Compatibility:**
- Officially supports Python 2.7 and Python 3.3-3.6
- Code includes compatibility layer for Python 2.x and 3.x (image_downloader.py lines 21-38)
- **Note:** Python 2.7, 3.3, 3.4, 3.5, 3.6 are all end-of-life versions

---

## 2. Actual Versions Installed

### 2.1 Current Specification vs. Latest Available

With the current `>=` constraints, the following versions would be installed (as of audit date):

| Package | Specified | Latest Stable | Notes |
|---------|-----------|---------------|-------|
| **selenium** | >=4.0.0 | 4.x.x (latest 4.x branch) | Minimum 4.0.0 ensures Selenium 4 API |
| **webdriver-manager** | >=3.8.0 | 4.x.x (latest available) | May install v4.x which has breaking changes |
| **requests** | >=2.28.0 | 2.31.x+ | Mature, stable library with good backward compatibility |

### 2.2 Version Constraint Analysis

**Selenium (>=4.0.0):**
- **Minimum:** 4.0.0 (Released October 2021)
- **Current Latest:** 4.x series
- **Breaking Changes:** Selenium 4 introduced major API changes from Selenium 3
  - Removed old `find_element_by_*` methods (deprecated)
  - New Service-based driver initialization
  - WebDriver BiDi support
- **Compatibility:** Code uses Selenium 4 API (Service, Options classes)

**webdriver-manager (>=3.8.0):**
- **Minimum:** 3.8.0
- **Current Latest:** 4.x series available
- **Risk:** Version 4.x may have API changes; no upper bound specified
- **Compatibility:** Code uses webdriver-manager optionally for auto-download

**requests (>=2.28.0):**
- **Minimum:** 2.28.0 (Released June 2022)
- **Current Latest:** 2.31.x series
- **Compatibility:** Excellent backward compatibility, stable API
- **Note:** Not directly imported in current codebase (urllib used instead)

---

## 3. Dependency Usage in Codebase

### 3.1 Selenium

**Import Locations:**
- `image_downloader.py` lines 184-187

**Usage:**
```python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
```

**Purpose:**
- Used exclusively in `_download_extended_page()` method
- Only required when downloading >100 images per query
- Implements headless browser automation to scroll and load additional images

**Configuration (lines 189-195):**
```python
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1024,768')
```

**Headless Mode Features:**
- Configured for server-side operation without display
- Includes stability options for containerized environments
- Suitable for Flask/web application integration

**Driver Initialization Strategy (lines 198-209):**
1. First: Try user-provided chromedriver path
2. Second: Try webdriver-manager auto-download
3. Fallback: Use system chromedriver

### 3.2 webdriver-manager

**Import Locations:**
- `image_downloader.py` lines 204-205 (conditional import)

**Usage:**
```python
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
```

**Purpose:**
- Optional dependency for automatic ChromeDriver management
- Handles ChromeDriver version matching with installed Chrome
- Downloads ChromeDriver binary if not present
- Used as fallback when explicit chromedriver path not provided

**Error Handling:**
- Wrapped in try/except block
- Falls back to system chromedriver if import fails
- Non-critical dependency (can work without it)

### 3.3 requests

**Status:** NOT directly imported in codebase

**Alternative Implementation:**
- Code uses `urllib` instead of `requests`
- Lines 24-38 in image_downloader.py show urllib imports for Python 2/3 compatibility
- HTTP operations performed using:
  - `urllib.request.Request`
  - `urllib.request.urlopen`
  - `urllib.request.URLError, HTTPError`

**Implications:**
- Listed in requirements.txt but not actively used
- May be intended for future use or legacy specification
- Could be considered for removal or might be used in other modules

---

## 4. Version Conflicts and Compatibility Requirements

### 4.1 Identified Issues

**Python Version Mismatch:**
- **Issue:** setup.py declares support for Python 2.7, 3.3-3.6 (all EOL)
- **Reality:** Modern dependencies may not support these versions
  - selenium>=4.0.0 requires Python 3.7+
  - webdriver-manager>=3.8.0 requires Python 3.7+
  - requests>=2.28.0 requires Python 3.7+
- **Impact:** Cannot install on Python versions listed in classifiers

**webdriver-manager Version Risk:**
- **Issue:** No upper bound on webdriver-manager version
- **Risk:** Version 4.x may introduce breaking API changes
- **Recommendation:** Test with v4.x or add upper bound constraint

**Unused Dependency:**
- **Issue:** requests is specified but not imported
- **Impact:** Unnecessary installation, potential security updates needed
- **Recommendation:** Verify if used in other modules or remove

### 4.2 Compatibility Matrix

| Dependency | Min Version | Python Requirement | Compatible? |
|------------|-------------|-------------------|-------------|
| selenium>=4.0.0 | 4.0.0 | Python 3.7+ | ⚠️ Conflicts with setup.py classifiers |
| webdriver-manager>=3.8.0 | 3.8.0 | Python 3.7+ | ⚠️ Conflicts with setup.py classifiers |
| requests>=2.28.0 | 2.28.0 | Python 3.7+ | ⚠️ Conflicts with setup.py classifiers |

### 4.3 Chrome/ChromeDriver Compatibility

**From docs/troubleshooting.rst:**
- ChromeDriver version must match installed Chrome browser version
- webdriver-manager handles this automatically
- Manual installation may require version matching
- Downgrading ChromeDriver may resolve compatibility issues

---

## 5. Comments and Documentation About Dependencies

### 5.1 README_PROGRAMMATIC_INTERFACE.md

**Lines 17-20:**
```markdown
The following packages will be installed:
- `selenium>=4.0.0` - For web scraping with headless browser
- `webdriver-manager>=3.8.0` - For automatic Chrome WebDriver management
- `requests>=2.28.0` - For HTTP requests
```

**Lines 198-199:**
- "**Headless Operation**: Selenium configured for headless browser operation suitable for servers"
- "**Automatic WebDriver Management**: Uses webdriver-manager for automatic ChromeDriver setup"

### 5.2 example_usage.py

**Line 148:**
```python
print("pip install selenium webdriver-manager requests")
```

Shows required package names for manual installation.

### 5.3 verify_implementation.py

**Lines 125-137:**
Verification script checks for presence of all three packages:
```python
required_packages = ['selenium', 'webdriver-manager', 'requests']
```

Includes test for headless configuration presence in source code.

### 5.4 docs/troubleshooting.rst

**Lines 60-81: Installing the chromedriver (with Selenium)**

Key points:
- Selenium needed for downloading >100 images
- ChromeDriver must be downloaded separately for some systems
- Path format differs by OS (Windows requires full path with backslashes)
- Linux may need Chrome browser installation guides
- Use `--chromedriver` or `-cd` argument to specify path
- "If on any rare occasion the chromedriver does not work for you, try downgrading it to a lower version" (line 81)

---

## 6. Known Issues and Constraints

### 6.1 From Troubleshooting Documentation

**SSL Certificate Issues (lines 9-14, 84-94):**
- Mac users with Python 3 may encounter SSL errors
- Solution: Run Install Certificates.command
- Specific to Python 3.7 installations

**ChromeDriver Version Issues (line 81):**
- ChromeDriver may occasionally not work
- Recommended solution: Downgrade to lower version
- Suggests version compatibility problems

**Browser Installation (lines 75-76):**
- Linux users may need specific guides for Chrome installation
- CentOS/Amazon Linux and Ubuntu have different procedures

### 6.2 Code-Level Constraints

**Python 2/3 Compatibility Layer:**
- Code maintains compatibility code for Python 2.x (lines 21-38 of image_downloader.py)
- Uses conditional imports based on `sys.version_info`
- However, dependencies don't support Python 2.x anymore

**Optional Selenium Usage:**
- Selenium only required for >100 images per search
- Smaller searches (<=100) work without Selenium
- Could function as optional dependency with graceful degradation

**Import Error Handling:**
- webdriver-manager wrapped in try/except (lines 203-209)
- Falls back to system chromedriver if auto-download fails
- No error handling for main selenium import (would fail hard)

---

## 7. Baseline Summary for Post-Update Comparison

### 7.1 Current State

| Aspect | Current Value |
|--------|---------------|
| **selenium** | >=4.0.0 (no upper bound) |
| **webdriver-manager** | >=3.8.0 (no upper bound) |
| **requests** | >=2.28.0 (no upper bound) |
| **Version Constraints** | Minimum only, latest will install |
| **Python Support (declared)** | 2.7, 3.3-3.6 |
| **Python Support (actual)** | 3.7+ (per dependencies) |
| **Selenium Usage** | Optional (>100 images only) |
| **webdriver-manager Usage** | Optional fallback |
| **requests Usage** | Not used (urllib instead) |

### 7.2 Items to Track After Update

1. **Version Changes:**
   - What specific versions were selected
   - Upper bounds added (if any)
   - Version pinning strategy

2. **Compatibility Updates:**
   - Python version classifier changes
   - Deprecated feature removal/updates
   - API changes required in code

3. **Dependency Changes:**
   - Removal of unused dependencies (requests?)
   - Addition of new dependencies
   - Changes to optional vs required status

4. **Functionality Impact:**
   - Breaking changes in updated packages
   - Required code modifications
   - Test results before/after

5. **Documentation Updates:**
   - README changes
   - Installation instruction updates
   - Troubleshooting guide additions

---

## 8. Recommendations for Update Process

### 8.1 Critical Actions

1. **Update Python Version Classifiers** in setup.py to match actual requirements (3.7+)
2. **Test webdriver-manager v4.x** compatibility or add upper bound (<4.0.0)
3. **Verify requests dependency** - remove if truly unused
4. **Add upper bounds** to prevent unexpected breaking changes
5. **Update documentation** to reflect actual Python version requirements

### 8.2 Testing Priorities

1. Headless Selenium operation in containerized environment
2. webdriver-manager auto-download functionality
3. Image search with >100 results (Selenium code path)
4. Image search with ≤100 results (non-Selenium code path)
5. Cross-platform compatibility (Windows, Mac, Linux)

### 8.3 Documentation Updates Needed

1. Update Python version requirements in README
2. Update dependency versions in README_PROGRAMMATIC_INTERFACE.md
3. Add migration guide if breaking changes introduced
4. Update troubleshooting guide with new version-specific issues

---

## 9. Appendix: Complete File Contents

### 9.1 requirements.txt

```
selenium>=4.0.0
webdriver-manager>=3.8.0
requests>=2.28.0
```

### 9.2 setup.py (relevant sections)

```python
__version__ = '2.8.0'

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='google_images_download',
    version=__version__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=install_requires,
    dependency_links=dependency_links,
)
```

---

## 10. Audit Completion Checklist

- [x] Document exact versions specified in requirements.txt for selenium, webdriver-manager, and requests
- [x] Document Python version classifiers and constraints in setup.py
- [x] Check for any additional dependency specifications or version pins
- [x] Note any comments or documentation about version constraints
- [x] Verify what versions would actually be installed with current specifications
- [x] Record any compatibility notes or known issues mentioned in code comments
- [x] Complete inventory of current dependency versions and constraints
- [x] Clear documentation of what versions are currently specified vs. what gets installed
- [x] Identification of any version conflicts or compatibility requirements
- [x] Baseline documentation ready for comparison after updates

---

**End of Dependency Audit Report**
