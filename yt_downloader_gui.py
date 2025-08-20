import sys
import os
import subprocess
import re
import threading
import tkinter.messagebox
import customtkinter as ctk

# --- Worker Thread for Downloading ---
# This class runs the download process in a separate thread.
# It communicates back to the main GUI thread using callbacks to prevent freezing.
class DownloadWorker(threading.Thread):
    def __init__(self, command, progress_callback, status_callback, finished_callback):
        super().__init__()
        self.command = command
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.finished_callback = finished_callback
        # Use a daemon thread so it automatically closes when the main app exits
        self.daemon = True

    def run(self):
        """
        Executes the yt-dlp command, captures its output in real-time,
        and uses callbacks to update the GUI.
        """
        try:
            # Popen allows us to read the output line-by-line in real time.
            # creationflags hides the console window on Windows.
            process = subprocess.Popen(
    self.command,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding='locale',  # or 'utf-8'
    errors='replace',
    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
)


            # Read stdout line by line to parse progress
            for line in iter(process.stdout.readline, ''):
                # Look for download progress percentage
                download_match = re.search(r"\[download\]\s+([0-9\.]+)%", line)
                if download_match:
                    percentage = float(download_match.group(1))
                    self.status_callback(f"Downloading... {percentage:.1f}%")
                    self.progress_callback(percentage)
                    continue

                # Look for post-processing steps
                if "[ExtractAudio]" in line:
                    self.status_callback("Extracting audio...")
                elif "[Merger]" in line:
                    self.status_callback("Merging video and audio...")

            # Wait for the process to finish and capture any errors
            stdout, stderr = process.communicate()
            return_code = process.returncode

            if return_code == 0:
                self.finished_callback(True, "Download completed successfully!")
            else:
                error_message = f"Download failed with exit code {return_code}.\n\nError:\n{stderr.strip()}"
                self.finished_callback(False, error_message)

        except Exception as e:
            self.finished_callback(False, f"An unexpected error occurred: {e}")


# --- Main Application Window ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Modern YouTube Downloader")
        self.geometry("700x420")
        ctk.set_appearance_mode("System")  # "Dark", "Light", or "System"
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # Give space to the status area

        # --- Main Frame ---
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)

        # --- Widgets ---
        # URL Input
        self.url_label = ctk.CTkLabel(main_frame, text="YouTube URL:", font=ctk.CTkFont(weight="bold"))
        self.url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter video or playlist URL")
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # Folder Input
        self.folder_label = ctk.CTkLabel(main_frame, text="Download Folder:", font=ctk.CTkFont(weight="bold"))
        self.folder_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.folder_entry = ctk.CTkEntry(main_frame)
        self.folder_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.browse_button = ctk.CTkButton(main_frame, text="Browse", width=100, command=self.browse_folder)
        self.browse_button.grid(row=1, column=2, padx=(0, 10), pady=10)

        # Quality and Options
        self.quality_label = ctk.CTkLabel(main_frame, text="Quality:", font=ctk.CTkFont(weight="bold"))
        self.quality_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.quality_combo = ctk.CTkComboBox(main_frame, values=[
            "Best", "Audio Only", "1080p", "720p", "480p", "360p"
        ])
        self.quality_combo.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.quality_combo.set("Best") # Default value

        self.playlist_checkbox = ctk.CTkCheckBox(main_frame, text="Download as Playlist")
        self.playlist_checkbox.grid(row=2, column=2, padx=10, pady=10, sticky="w")

        # --- Status Display Area ---
        self.status_label = ctk.CTkLabel(self, text="Status: Idle", text_color="gray")
        self.status_label.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")

        self.progress_bar = ctk.CTkProgressBar(self, mode='determinate')
        self.progress_bar.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.progress_bar.set(0)

        # --- Download Button ---
        self.download_button = ctk.CTkButton(self, text="Download", font=ctk.CTkFont(size=14, weight="bold"), command=self.start_download)
        self.download_button.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        # --- Initialize ---
        self.setup_default_folder()
        self.worker = None

    def setup_default_folder(self):
        """Sets the default download folder and creates it if it doesn't exist."""
        default_folder = os.path.join("D:\\", "youtube downloads")
        try:
            os.makedirs(default_folder, exist_ok=True)
            self.folder_entry.insert(0, default_folder)
        except OSError as e:
            tkinter.messagebox.showwarning("Folder Error", f"Could not create default folder {default_folder}:\n{e}")
            self.folder_entry.insert(0, os.path.expanduser("~"))

    def browse_folder(self):
        folder = ctk.filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, 'end')
            self.folder_entry.insert(0, folder)

    def set_controls_enabled(self, enabled):
        """Enable or disable GUI controls during download."""
        state = "normal" if enabled else "disabled"
        self.url_entry.configure(state=state)
        self.folder_entry.configure(state=state)
        self.browse_button.configure(state=state)
        self.quality_combo.configure(state=state)
        self.playlist_checkbox.configure(state=state)
        self.download_button.configure(state=state)

    def start_download(self):
        if self.worker is not None and self.worker.is_alive():
            tkinter.messagebox.showwarning("Busy", "A download is already in progress.")
            return

        url = self.url_entry.get().strip()
        folder = self.folder_entry.get().strip()

        if not url or not folder:
            tkinter.messagebox.showerror("Input Error", "Please provide a URL and a download folder.")
            return

        exe_path = os.path.join(os.getcwd(), "yt-dlp.exe")
        if not os.path.exists(exe_path):
            tkinter.messagebox.showerror("Error", "'yt-dlp.exe' not found in the application directory!")
            return

        # --- Build yt-dlp Command ---
        quality = self.quality_combo.get()
        if quality == "Best":
            format_args = ["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"]
        elif quality == "Audio Only":
            format_args = ["-f", "bestaudio", "-x", "--audio-format", "mp3"]
        else: # e.g., "1080p"
            height = quality.replace("p", "")
            format_args = ["-f", f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"]

        is_playlist = self.playlist_checkbox.get()
        output_template = os.path.join(folder, "%(playlist_index)s - %(title)s.%(ext)s" if is_playlist else "%(title)s.%(ext)s")

        command = [
            exe_path,
            "--ffmpeg-location", script_dir, 
            *format_args,
            "-o", output_template,
            "--progress", "--newline", # Essential for progress parsing
            url,
            "--yes-playlist" if is_playlist else "--no-playlist"
        ]

        # --- UI Updates & Worker Start ---
        self.set_controls_enabled(False)
        self.progress_bar.set(0)
        self.status_label.configure(text="Status: Preparing...", text_color="white")

        self.worker = DownloadWorker(command, self.update_progress, self.update_status, self.on_download_finished)
        self.worker.start()

    def update_progress(self, percentage):
        """Callback to update the progress bar from the worker thread."""
        # The progress bar expects a value between 0.0 and 1.0
        self.progress_bar.set(percentage / 100.0)

    def update_status(self, message):
        """Callback to update the status label."""
        self.status_label.configure(text=f"Status: {message}")

    def on_download_finished(self, success, message):
        """Callback for when the download is complete."""
        self.set_controls_enabled(True)
        if success:
            self.status_label.configure(text="Status: Finished!", text_color="lightgreen")
            self.progress_bar.set(1)
            tkinter.messagebox.showinfo("Success", message)
        else:
            self.status_label.configure(text="Status: Error!", text_color="red")
            self.progress_bar.set(0)
            tkinter.messagebox.showerror("Error", message)
        
        # Reset for next download
        self.after(3000, self.reset_status)

    def reset_status(self):
        """Resets the status labels after a delay."""
        self.status_label.configure(text="Status: Idle", text_color="gray")
        self.progress_bar.set(0)

if __name__ == "__main__":
    app = App()
    app.mainloop()