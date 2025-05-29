# YTDLP-NG
Another Simple GUI for YT-DLP

# yt-dlp GUI Downloader

A simple Python Tkinter-based graphical user interface (GUI) for `yt-dlp`, allowing users to easily fetch video format information from YouTube URLs, select desired formats, and download them. It also provides a quick option to download the best available audio as an MP3.

This project was created with the assistance of an AI Language Model.

## Features

* **User-Friendly Interface:** Simple GUI built with Tkinter and ttk for a cleaner look.
* **Specify `yt-dlp` Path:** Allows users to browse and set the path to their `yt-dlp` executable.
* **Format Listing:** Fetches and displays a detailed list of all available video and audio formats for a given YouTube URL, including:
    * Format ID
    * Extension (e.g., mp4, webm)
    * Resolution or Audio Bitrate
    * FPS (Frames Per Second)
    * Type (Video+Audio, Video Only, Audio Only)
    * Video and Audio Codecs
    * Approximate Filesize
    * Format notes from `yt-dlp`
* **Selective Download:** Users can select one or multiple formats from the list to download.
* **Quick Audio Download:** A dedicated button to download the best available audio and convert it to MP3 format (requires FFmpeg).
* **Download Directory Selection:** Users can specify a directory where downloaded files will be saved.
* **Persistent Configuration:** Saves the `yt-dlp` path and download directory in a `yt_dlp_gui_config.json` file for future sessions.
* **Status Updates:** A status bar provides feedback on current operations (fetching, downloading, errors).
* **Cross-Platform (with caveats):** Written in Python, it should run on Linux, Windows, and macOS, provided Python and Tkinter are installed. The `creationflags` for subprocess are set to avoid console windows on Windows.
* **Error Handling:** Basic error messages for common issues (e.g., invalid paths, network errors, `yt-dlp` failures). Detailed `yt-dlp` errors are printed to the console.
* **Threaded Operations:** Network operations (fetching formats, downloading) are performed in separate threads to keep the GUI responsive.

## Prerequisites

1.  **Python 3:** Ensure you have Python 3 installed on your system. Tkinter is usually included with standard Python installations. If not, you may need to install it separately (e.g., `sudo apt-get install python3-tk` on Debian/Ubuntu).
2.  **`yt-dlp` Executable:**
    * Download the latest `yt-dlp` executable for your system (e.g., `yt-dlp_linux`, `yt-dlp.exe`) from the [official yt-dlp repository](https://github.com/yt-dlp/yt-dlp#installation).
    * Make sure the downloaded file is executable (e.g., `chmod +x yt-dlp_linux` on Linux/macOS).
3.  **`ffmpeg` (Recommended, especially for audio extraction):**
    * For audio extraction (like the "Download Audio Only (Best MP3)" feature) and for `yt-dlp` to merge separate video and audio streams (often required for the highest quality formats), `ffmpeg` is necessary.
    * Download `ffmpeg` from [ffmpeg.org](https://ffmpeg.org/download.html) and ensure it's either in your system's PATH or in the same directory as your `yt-dlp` executable.

## Installation

1.  **Save the Script:** Download or copy the Python script (e.g., `yt_dlp_gui.py`) to a directory on your computer.
2.  **Place `yt-dlp`:** You can place your `yt-dlp` executable anywhere, as you will specify its path in the GUI. For convenience, you might place it in the same directory as the script or a dedicated tools directory.

No further installation steps are typically required for the script itself, as it uses standard Python libraries.

## How to Use

1.  **Run the Application:**
    Open a terminal or command prompt, navigate to the directory where you saved `yt_dlp_gui.py`, and run the script:
    ```bash
    python3 yt_dlp_gui.py
    ```
    (or `python yt_dlp_gui.py` if `python` points to Python 3).

2.  **Set `yt-dlp` Path (First Time):**
    * The application window will open.
    * In the "yt-dlp Executable Path" section, click the "Browse" button.
    * Navigate to and select your `yt-dlp` executable file (e.g., `yt-dlp_linux`).
    * This path will be saved in `yt_dlp_gui_config.json` for future use.

3.  **Set Download Directory:**
    * In the "Download Directory" section, the application will try to default to your system's "Downloads" folder or the current working directory.
    * You can change this by clicking "Browse" and selecting your preferred directory for saving downloaded files. This is also saved.

4.  **Enter YouTube URL:**
    * Paste the full URL of the YouTube video you want to download into the "YouTube Video URL" field.

5.  **Fetch Formats:**
    * Click the "Fetch Available Formats" button.
    * The application will run `yt-dlp` in the background. The status bar will indicate it's "Fetching formats...".
    * Once complete, the "Available Formats" listbox will populate with all detected video and audio streams.

6.  **Select Formats for Download:**
    * Review the list of formats.
    * Click on a format to select it.
    * To select multiple formats:
        * **Ctrl+Click** (Windows/Linux) or **Cmd+Click** (macOS) to select/deselect individual items.
        * **Shift+Click** to select a range of items.

7.  **Download:**
    * **To download the selected video/audio formats:**
        * Ensure you have one or more formats selected in the list.
        * Click the "Download Selected" button.
        * The status bar will show progress for each selected download. Files will be saved in your chosen download directory, with the format ID appended to the filename (e.g., `VideoTitle.137.mp4`) to differentiate them.
    * **To download audio only (as MP3):**
        * Click the "Download Audio Only (Best MP3)" button.
        * This will instruct `yt-dlp` to download the best quality audio and convert it to an MP3 file. This does not require a selection from the list. The file will be named like `VideoTitle.mp3`. (Requires `ffmpeg`).

8.  **Check Status and Output:**
    * The status bar at the bottom of the window provides real-time updates on the application's actions.
    * If `yt-dlp` encounters errors during fetching or downloading, a summary might be shown in the status bar or a dialog box. For complete error details, check the terminal/console window from which you launched the Python script.

9.  **Closing the Application:**
    * When you close the application window, your current `yt-dlp` path and download directory settings are automatically saved to `yt_dlp_gui_config.json`.

## Troubleshooting

* **"yt-dlp executable path is invalid"**: Ensure the path you've set for `yt-dlp` is correct and that the file is executable.
* **"No formats found"**: The video URL might be incorrect, private, or `yt-dlp` might be blocked or outdated. Try updating `yt-dlp`.
* **Audio download/conversion fails**: Make sure `ffmpeg` is installed and accessible by `yt-dlp` (either in PATH or same directory as `yt-dlp`).
* **GUI freezes (unlikely but possible)**: If a download takes an extremely long time or an unexpected error occurs in the threading, the GUI might become less responsive. Check the console for errors. The application includes timeouts for operations.
* **"yt-dlp executable not found"**: Double-check the path provided. If `yt-dlp` was moved or deleted, you'll need to set the path again.

## Contributing

This is a simple utility. Suggestions for improvements or bug fixes can be made by modifying the script. Consider features like:
* Progress bars for downloads (requires more complex parsing of `yt-dlp` output).
* Queueing multiple URLs.
* More advanced `yt-dlp` option integration.

---

This README provides a comprehensive guide to using the yt-dlp GUI Downloader.

