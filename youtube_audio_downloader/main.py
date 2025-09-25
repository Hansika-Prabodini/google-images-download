"""
YouTube Audio Downloader - Main Application Entry Point

This module provides the main application class and entry point for the YouTube Audio Downloader.
It includes GUI components, download logic, and utility functions with proper separation of concerns.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import os
import sys
import platform


class YouTubeAudioDownloader:
    """
    Main application class for YouTube Audio Downloader.
    
    Provides a GUI interface for downloading audio from YouTube videos
    with cross-platform compatibility and Downloads folder detection.
    """
    
    def __init__(self, root=None):
        """Initialize the YouTube Audio Downloader application."""
        if root is None:
            root = tk.Tk()
        
        self.root = root
        self.root.title("YouTube Audio Downloader")
        self.root.geometry("600x400")
        
        # Initialize download path to user's Downloads folder
        self.download_path = self._get_downloads_folder()
        
        self._setup_gui()
    
    def _get_downloads_folder(self):
        """
        Get the user's Downloads folder path using pathlib for cross-platform compatibility.
        
        Returns:
            Path: Path to the Downloads folder, falls back to user home if not found
        """
        try:
            # Get user home directory
            home = Path.home()
            
            # Check for Downloads folder (common across Windows, macOS, Linux)
            downloads_folder = home / "Downloads"
            
            if downloads_folder.exists() and downloads_folder.is_dir():
                return downloads_folder
            else:
                # Fallback to home directory if Downloads folder doesn't exist
                return home
                
        except Exception as e:
            # Ultimate fallback to current working directory
            print(f"Warning: Could not determine Downloads folder: {e}")
            return Path.cwd()
    
    def _setup_gui(self):
        """Set up the graphical user interface components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL input section
        url_label = ttk.Label(main_frame, text="YouTube URL:")
        url_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Download path section
        path_label = ttk.Label(main_frame, text="Download Location:")
        path_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.path_var = tk.StringVar(value=str(self.download_path))
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=40)
        path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        browse_button = ttk.Button(path_frame, text="Browse", command=self._browse_folder)
        browse_button.grid(row=0, column=1, padx=(5, 0))
        
        # Download button
        download_button = ttk.Button(main_frame, text="Download Audio", command=self._download_audio)
        download_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Status/Log area
        status_label = ttk.Label(main_frame, text="Status:")
        status_label.grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        
        # Text area with scrollbar for status messages
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.status_text = tk.Text(text_frame, height=10, width=50, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        path_frame.columnconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self._log_message("YouTube Audio Downloader initialized successfully.")
        self._log_message(f"Default download location: {self.download_path}")
        self._log_platform_info()
    
    def _log_platform_info(self):
        """Log platform and compatibility information."""
        system_info = f"Platform: {platform.system()} {platform.release()}"
        python_info = f"Python: {sys.version.split()[0]}"
        
        self._log_message(system_info)
        self._log_message(python_info)
        
        # Check Python version compatibility
        version_info = sys.version_info
        if version_info < (3, 7):
            self._log_message("WARNING: yt-dlp requires Python 3.7+. Current version may not be supported.", level="warning")
        else:
            self._log_message("Python version is compatible with yt-dlp requirements.")
    
    def _browse_folder(self):
        """Open folder browser dialog to select download location."""
        folder_path = filedialog.askdirectory(
            title="Select Download Location",
            initialdir=str(self.download_path)
        )
        
        if folder_path:
            self.path_var.set(folder_path)
            self.download_path = Path(folder_path)
            self._log_message(f"Download location changed to: {folder_path}")
    
    def _download_audio(self):
        """Handle audio download process (placeholder implementation)."""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        if not self.download_path.exists():
            messagebox.showerror("Error", "Selected download path does not exist")
            return
        
        # Placeholder implementation - actual yt-dlp integration would go here
        self._log_message(f"Starting download from: {url}")
        self._log_message(f"Download location: {self.download_path}")
        self._log_message("Note: This is a placeholder. Actual download functionality requires yt-dlp integration.")
        
        # TODO: Implement actual download logic with yt-dlp
        # This would include:
        # - URL validation
        # - yt-dlp configuration
        # - Progress tracking
        # - Error handling
        # - File conversion/format selection
    
    def _log_message(self, message, level="info"):
        """
        Add a message to the status log.
        
        Args:
            message (str): The message to log
            level (str): Log level ('info', 'warning', 'error')
        """
        self.status_text.config(state=tk.NORMAL)
        
        # Add timestamp and level prefix
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        level_prefix = f"[{level.upper()}]" if level != "info" else ""
        
        formatted_message = f"[{timestamp}] {level_prefix} {message}\n"
        
        self.status_text.insert(tk.END, formatted_message)
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        
        # Update the GUI
        self.root.update_idletasks()
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()


def verify_imports():
    """
    Verify that all required modules can be imported successfully.
    
    Returns:
        dict: Dictionary containing import status and any error messages
    """
    import_status = {
        'tkinter': {'success': False, 'error': None},
        'pathlib': {'success': False, 'error': None},
        'platform_detection': {'success': False, 'error': None, 'downloads_folder': None}
    }
    
    # Test tkinter import
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        # Test basic tkinter functionality
        root = tk.Tk()
        root.withdraw()  # Don't show the window
        root.destroy()
        import_status['tkinter']['success'] = True
    except Exception as e:
        import_status['tkinter']['error'] = str(e)
    
    # Test pathlib import and functionality
    try:
        from pathlib import Path
        import os
        
        # Test basic pathlib operations
        home = Path.home()
        downloads = home / "Downloads"
        current_dir = Path.cwd()
        
        import_status['pathlib']['success'] = True
        
        # Test Downloads folder detection
        if downloads.exists() and downloads.is_dir():
            import_status['platform_detection']['downloads_folder'] = str(downloads)
            import_status['platform_detection']['success'] = True
        else:
            import_status['platform_detection']['downloads_folder'] = str(home)
            import_status['platform_detection']['success'] = True
            
    except Exception as e:
        import_status['pathlib']['error'] = str(e)
        import_status['platform_detection']['error'] = str(e)
    
    return import_status


def main():
    """Main entry point for the YouTube Audio Downloader application."""
    print("YouTube Audio Downloader - Starting...")
    
    # Verify imports before starting GUI
    print("Verifying system compatibility...")
    import_status = verify_imports()
    
    # Report import status
    for module, status in import_status.items():
        if status['success']:
            print(f"✓ {module}: OK")
            if module == 'platform_detection' and status.get('downloads_folder'):
                print(f"  Downloads folder: {status['downloads_folder']}")
        else:
            print(f"✗ {module}: FAILED - {status['error']}")
    
    # Check if critical imports failed
    if not import_status['tkinter']['success']:
        print("\nERROR: tkinter is not available. This is required for the GUI.")
        print("Please ensure tkinter is installed (usually comes with Python).")
        sys.exit(1)
    
    if not import_status['pathlib']['success']:
        print("\nERROR: pathlib is not available. This is required for file operations.")
        print("Please ensure you're using Python 3.4+ (pathlib is included in standard library).")
        sys.exit(1)
    
    print("\nSystem compatibility check passed. Starting GUI...")
    
    try:
        # Create and run the application
        app = YouTubeAudioDownloader()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
