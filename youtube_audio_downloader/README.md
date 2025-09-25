# YouTube Audio Downloader

A Python application for downloading audio from YouTube videos with a simple GUI interface.

## Python Version Compatibility

### Requirements

- **Minimum Python Version**: Python 3.7+
- **Recommended**: Python 3.8+

### Compatibility Notes

#### Core Dependencies
- **tkinter**: Included with Python standard library (Python 2.7+, 3.x)
- **pathlib**: Included with Python standard library (Python 3.4+)
- **yt-dlp**: Requires Python 3.7+ (external dependency)

#### Platform Support
- **Windows**: Tested with Python 3.7+
- **macOS**: Tested with Python 3.7+ 
- **Linux**: Tested with Python 3.7+

### Version Compatibility Matrix

| Python Version | Core Features | yt-dlp Support | Status |
|---------------|---------------|----------------|---------|
| 3.6 and below | ✗ | ✗ | Not Supported |
| 3.7 | ✓ | ✓ | Supported |
| 3.8 | ✓ | ✓ | Supported |
| 3.9 | ✓ | ✓ | Supported |
| 3.10+ | ✓ | ✓ | Supported |

### Installation

1. Ensure Python 3.7+ is installed:
   ```bash
   python --version  # Should show 3.7.0 or higher
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify installation:
   ```bash
   python test_youtube_downloader_setup.py
   ```

4. Run the application:
   ```bash
   python -m youtube_audio_downloader.main
   ```

## Features

### Cross-Platform Downloads Folder Detection

The application automatically detects the user's Downloads folder across different operating systems:

- **Windows**: `C:\Users\[Username]\Downloads`
- **macOS**: `/Users/[Username]/Downloads`  
- **Linux**: `/home/[Username]/Downloads`

If the Downloads folder is not found, the application falls back to:
1. User's home directory
2. Current working directory (as last resort)

### GUI Components

- **URL Input**: Enter YouTube video URLs
- **Download Location**: Browse and select download directory
- **Status Log**: Real-time status updates and system information
- **Cross-platform File Dialog**: Native file browser integration

### System Compatibility Verification

The application includes built-in compatibility checks for:

- Python version requirements
- tkinter availability and functionality
- pathlib cross-platform file operations
- Downloads folder detection
- Module structure validation

## Architecture

### Module Structure

```
youtube_audio_downloader/
├── __init__.py          # Package initialization and exports
├── main.py              # Main application entry point
└── README.md            # This documentation
```

### Separation of Concerns

- **GUI Layer**: tkinter interface components
- **Download Logic**: yt-dlp integration (placeholder)
- **Utility Functions**: Cross-platform file operations
- **Verification**: System compatibility testing

## Development

### Testing

Run the compatibility test suite:
```bash
python test_youtube_downloader_setup.py
```

### Adding New Features

When adding new functionality:

1. Maintain Python 3.7+ compatibility
2. Use pathlib for all file operations
3. Test across platforms (Windows, macOS, Linux)
4. Update compatibility documentation

## Troubleshooting

### Common Issues

#### "tkinter not available"
- **Linux**: Install `python3-tk` package
  ```bash
  sudo apt-get install python3-tk  # Ubuntu/Debian
  sudo yum install tkinter         # RHEL/CentOS
  ```
- **macOS**: tkinter should be included with Python
- **Windows**: tkinter is included with standard Python installation

#### "yt-dlp requires Python 3.7+"
- Upgrade Python to version 3.7 or higher
- Use `python --version` to check current version
- Consider using pyenv or conda for version management

#### Downloads folder not found
- Application will automatically fall back to home directory
- Manually select download location using "Browse" button
- Verify folder permissions for write access

## Future Enhancements

- [ ] Complete yt-dlp integration
- [ ] Audio format selection (MP3, AAC, etc.)
- [ ] Batch download support  
- [ ] Download progress tracking
- [ ] Playlist support
- [ ] Quality selection options
