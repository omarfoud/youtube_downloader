# Modern YouTube Downloader GUI

A simple, modern-looking GUI application for downloading YouTube videos and playlists, built with Python, CustomTkinter, and the powerful `yt-dlp` command-line tool.


*(Image of the application interface: URL field, folder selection, quality dropdown, status bar, and download button)*

## Features

- **Modern UI**: Clean, theme-aware interface that supports both light and dark modes.
- **Download Videos & Playlists**: Easily download single videos or entire playlists.
- **Selectable Quality**: Choose from various quality options, including Best, 1080p, 720p, etc.
- **Audio-Only Mode**: Extract and download audio in MP3 format.
- **Real-time Progress**: A progress bar and status label provide real-time feedback on the download process.
- **Cross-Platform**: Built with Python and Tkinter, it's designed to run on Windows, macOS, and Linux.
- **Standalone Dependencies**: The application is designed to work with `yt-dlp.exe` and `ffmpeg` placed in its directory, making it semi-portable.

## Prerequisites

Before you can run this application, you need to have the following software installed and configured.

### 1. Python
- **Python 3.7+** is required. You can download it from [python.org](https://www.python.org/downloads/).
- Make sure to check the box **"Add Python to PATH"** during installation.

### 2. External Binaries (Crucial!)
This application is a graphical front-end for `yt-dlp` and requires `ffmpeg` for processing media files.

- **`yt-dlp`**:
    1. Go to the [yt-dlp latest releases page](https://github.com/yt-dlp/yt-dlp/releases/latest).
    2. Download `yt-dlp.exe` (for Windows) or the appropriate binary for your OS.
    3. **Place the downloaded file (`yt-dlp.exe`) in the same directory as the `yt_downloader_gui.py` script.**

- **`ffmpeg`**:
    1. **For Windows:** Download a build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) (the "essentials" release is sufficient).
    2. **For other OS:** Use a package manager (e.g., `sudo apt install ffmpeg` on Debian/Ubuntu, `brew install ffmpeg` on macOS).
    3. **Crucially, ensure `ffmpeg.exe` (or `ffmpeg`) is accessible.** The easiest way for this script to work is to:
        - **(Windows)** Extract the downloaded archive and place `ffmpeg.exe` and `ffprobe.exe` from the `bin` folder into the same directory as the `yt_downloader_gui.py` script.

Your project folder should look like this:
```
/your-project-folder
├── yt_downloader_gui.py
├── yt-dlp.exe
├── ffmpeg.exe
├── ffprobe.exe
└── ... (other files)
```
2.  **Set up a Virtual Environment (Recommended):**
    ```bash
    # Create a virtual environment
    python -m venv venv

    # Activate it
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Python Dependencies:**
    Create a `requirements.txt` file with the content `customtkinter` or simply run:
    ```bash
    pip install customtkinter
    ```

## How to Run

Once all prerequisites and dependencies are in place, run the application from your terminal:

```bash
python yt_downloader_gui.py
```

## How to Use

1.  **Paste URL**: Copy the URL of the YouTube video or playlist you want to download and paste it into the "YouTube URL" field.
2.  **Choose Folder**: Click "Browse" to select a folder where your downloads will be saved. The application defaults to `D:\youtube downloads` on Windows if available.
3.  **Select Quality**:
    - `Best`: Downloads the best available MP4 video with audio.
    - `Audio Only`: Downloads the best audio and converts it to an MP3 file.
    - `1080p`, `720p`, etc.: Downloads the best video up to the selected resolution.
4.  **Playlist Option**: If the URL is for a playlist, check the "Download as Playlist" box to download all videos. Files will be prefixed with their index number.
5.  **Download**: Click the "Download" button to begin.
6.  **Monitor Progress**: Watch the progress bar and status label for real-time updates. You will be notified when the download is complete or if an error occurs.
