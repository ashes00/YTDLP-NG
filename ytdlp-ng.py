import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import threading
import datetime
import json 
import shutil # For shutil.which
import webbrowser # For opening download links

class YTDLP_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("yt-dlp GUI Downloader")
        
        self.root.geometry("1100x780") 
        try:
            self.root.state('zoomed') 
        except tk.TclError:
            try:
                self.root.attributes('-zoomed', True)
            except tk.TclError:
                print("Could not apply maximized state via 'zoomed' or attributes.")
        
        self.yt_dlp_path_var = tk.StringVar(value="yt-dlp_linux")
        self.ffmpeg_path_var = tk.StringVar(value="ffmpeg") 
        self.url_var = tk.StringVar()
        self.download_dir_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.download_option_var = tk.StringVar(value="selected") 
        
        self.selected_custom_video_details_var = tk.StringVar(value="")
        self.selected_custom_audio_details_var = tk.StringVar(value="")
        self.video_title = "Untitled Video" 

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        top_bar_frame = ttk.Frame(main_frame)
        top_bar_frame.pack(fill=tk.X, pady=(0, 5))
        self.quit_button = ttk.Button(top_bar_frame, text="Quit Application", command=self.quit_application)
        self.quit_button.pack(side=tk.RIGHT, padx=5)

        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=5)
        config_frame.columnconfigure(1, weight=1) 
        config_frame.columnconfigure(3, weight=0) 

        # yt-dlp Path
        ttk.Label(config_frame, text="yt-dlp Path:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.yt_dlp_path_entry = ttk.Entry(config_frame, textvariable=self.yt_dlp_path_var, width=45)
        self.yt_dlp_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.browse_yt_dlp_button = ttk.Button(config_frame, text="Browse...", command=self.browse_yt_dlp_path)
        self.browse_yt_dlp_button.grid(row=0, column=2, padx=5, pady=5)
        self.yt_dlp_status_label = ttk.Label(config_frame, text="", wraplength=200)
        self.yt_dlp_status_label.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)


        # ffmpeg Path
        ttk.Label(config_frame, text="ffmpeg Path:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.ffmpeg_path_entry = ttk.Entry(config_frame, textvariable=self.ffmpeg_path_var, width=45)
        self.ffmpeg_path_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.browse_ffmpeg_button = ttk.Button(config_frame, text="Browse...", command=self.browse_ffmpeg_path)
        self.browse_ffmpeg_button.grid(row=1, column=2, padx=5, pady=5)
        self.ffmpeg_status_label = ttk.Label(config_frame, text="", wraplength=200)
        self.ffmpeg_status_label.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)

        # YouTube URL
        ttk.Label(config_frame, text="YouTube URL:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.url_entry = ttk.Entry(config_frame, textvariable=self.url_var, width=45)
        self.url_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.fetch_button = ttk.Button(config_frame, text="Fetch Formats", command=self.fetch_formats_async)
        self.fetch_button.grid(row=2, column=2, padx=5, pady=5, sticky=tk.EW, columnspan=2) 

        # Download Directory
        ttk.Label(config_frame, text="Download To:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.download_dir_label = ttk.Label(config_frame, textvariable=self.download_dir_var, relief=tk.SUNKEN, padding=2)
        self.download_dir_label.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        self.choose_dir_button = ttk.Button(config_frame, text="Choose Dir...", command=self.choose_download_dir)
        self.choose_dir_button.grid(row=3, column=2, padx=5, pady=5, sticky=tk.EW, columnspan=2) 

        formats_frame = ttk.LabelFrame(main_frame, text="Available Formats", padding="10")
        formats_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        formats_frame.columnconfigure(0, weight=1)
        formats_frame.rowconfigure(0, weight=1)

        self.formats_listbox = tk.Listbox(formats_frame, selectmode=tk.MULTIPLE, height=20, exportselection=False) 
        self.formats_listbox.grid(row=0, column=0, sticky=tk.NSEW)
        self.formats_listbox.bind('<<ListboxSelect>>', self.on_format_selection_change) 
        
        formats_scrollbar_y = ttk.Scrollbar(formats_frame, orient=tk.VERTICAL, command=self.formats_listbox.yview)
        formats_scrollbar_y.grid(row=0, column=1, sticky=tk.NS)
        self.formats_listbox.configure(yscrollcommand=formats_scrollbar_y.set)

        formats_scrollbar_x = ttk.Scrollbar(formats_frame, orient=tk.HORIZONTAL, command=self.formats_listbox.xview)
        formats_scrollbar_x.grid(row=1, column=0, sticky=tk.EW)
        self.formats_listbox.configure(xscrollcommand=formats_scrollbar_x.set)
        self.format_data = [] 

        download_options_frame = ttk.LabelFrame(main_frame, text="Download Options", padding="10")
        download_options_frame.pack(fill=tk.X, pady=5)
        download_options_frame.columnconfigure(0, weight=0) 
        download_options_frame.columnconfigure(1, weight=0) 
        download_options_frame.columnconfigure(2, weight=0) 
        download_options_frame.columnconfigure(3, weight=1) 


        self.selected_format_radio = ttk.Radiobutton(download_options_frame, text="Selected Format(s) from List", variable=self.download_option_var, value="selected", command=self.on_download_option_change)
        self.selected_format_radio.grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        
        self.custom_merge_radio = ttk.Radiobutton(download_options_frame, text="Custom Video+Audio Merge (MP4)", variable=self.download_option_var, value="custom_merge_mp4", command=self.on_download_option_change)
        self.custom_merge_radio.grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        
        self.audio_only_radio = ttk.Radiobutton(download_options_frame, text="Audio Only (best, mp3)", variable=self.download_option_var, value="audio_mp3", command=self.on_download_option_change)
        self.audio_only_radio.grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        
        self.download_button = ttk.Button(download_options_frame, text="Download", command=self.download_async)
        self.download_button.grid(row=0, column=1, rowspan=3, padx=(10,5), pady=5, sticky=tk.NSEW) 

        self.custom_video_label = ttk.Label(download_options_frame, text="Custom Video:")
        self.custom_video_label.grid(row=0, column=2, padx=(10,2), pady=1, sticky=tk.W)
        self.custom_video_details_label = ttk.Label(download_options_frame, textvariable=self.selected_custom_video_details_var, foreground="blue", wraplength=0) 
        self.custom_video_details_label.grid(row=0, column=3, padx=2, pady=1, sticky=tk.W)

        self.custom_audio_label = ttk.Label(download_options_frame, text="Custom Audio:")
        self.custom_audio_label.grid(row=1, column=2, padx=(10,2), pady=1, sticky=tk.W)
        self.custom_audio_details_label = ttk.Label(download_options_frame, textvariable=self.selected_custom_audio_details_var, foreground="blue", wraplength=0) 
        self.custom_audio_details_label.grid(row=1, column=3, padx=2, pady=1, sticky=tk.W)
        
        self.custom_video_label.grid_remove()
        self.custom_video_details_label.grid_remove()
        self.custom_audio_label.grid_remove()
        self.custom_audio_details_label.grid_remove()


        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD, state=tk.DISABLED) 
        self.log_text.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)
        
        log_buttons_frame = ttk.Frame(log_frame)
        log_buttons_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(5,0))
        log_buttons_frame.columnconfigure(0, weight=1) 
        log_buttons_frame.columnconfigure(1, weight=1)

        self.clear_log_button = ttk.Button(log_buttons_frame, text="Clear Log", command=self.clear_log)
        self.clear_log_button.pack(side=tk.LEFT, padx=5)
        
        self.copy_log_button = ttk.Button(log_buttons_frame, text="Copy Log", command=self.copy_log_to_clipboard)
        self.copy_log_button.pack(side=tk.RIGHT, padx=5)
        
        self.update_log("Ready.")
        self.perform_initial_checks()


    def perform_initial_checks(self):
        """Performs pre-flight checks for executables on startup."""
        self.check_executable_path('yt-dlp', self.yt_dlp_path_var.get(), self.yt_dlp_status_label, 
                                   "https://github.com/yt-dlp/yt-dlp#installation") # CORRECTED URL
        self.check_executable_path('ffmpeg', self.ffmpeg_path_var.get(), self.ffmpeg_status_label, 
                                   "https://ffmpeg.org/download.html") # CORRECTED URL

    def check_executable_path(self, name, path_to_check, status_label_widget, download_url):
        """Checks if an executable is found and valid, updates status label."""
        status_label_widget.unbind("<Button-1>") 
        status_label_widget.config(cursor="")

        found_in_path = False
        is_file_and_executable = False

        if os.path.isfile(path_to_check):
            if os.name == 'nt' or os.access(path_to_check, os.X_OK): 
                is_file_and_executable = True
        
        if not is_file_and_executable:
            which_path = shutil.which(path_to_check)
            if which_path:
                path_to_check = which_path 
                if os.name == 'nt' or os.access(path_to_check, os.X_OK):
                    is_file_and_executable = True
                    found_in_path = True
        
        if is_file_and_executable:
            status_text = f"{name} OK"
            if found_in_path : status_text += " (in PATH)"
            status_label_widget.config(text=status_text, foreground="green", font=('TkDefaultFont', 9, 'normal'))
        else:
            status_label_widget.config(text=f"{name} not found. Download", 
                                       foreground="blue", font=('TkDefaultFont', 9, 'underline'))
            status_label_widget.bind("<Button-1>", lambda e, url=download_url: self.open_link(url))
            status_label_widget.config(cursor="hand2")

    def open_link(self, url):
        """Opens the given URL in a new web browser tab."""
        try:
            webbrowser.open_new_tab(url)
            self.update_log(f"Opened link: {url}")
        except Exception as e:
            self.update_log(f"Error opening link {url}: {e}")
            messagebox.showerror("Error Opening Link", f"Could not open the link: {e}")


    def on_download_option_change(self):
        if self.download_option_var.get() == "custom_merge_mp4":
            self.custom_video_label.grid()
            self.custom_video_details_label.grid()
            self.custom_audio_label.grid()
            self.custom_audio_details_label.grid()
            self.update_custom_selection_display() 
        else:
            self.custom_video_label.grid_remove()
            self.custom_video_details_label.grid_remove()
            self.custom_audio_label.grid_remove()
            self.custom_audio_details_label.grid_remove()
            self.selected_custom_video_details_var.set("")
            self.selected_custom_audio_details_var.set("")

    def on_format_selection_change(self, event=None):
        if self.download_option_var.get() == "custom_merge_mp4":
            self.update_custom_selection_display()

    def update_custom_selection_display(self):
        selected_indices = self.formats_listbox.curselection()
        self.selected_custom_video_details_var.set("") 
        self.selected_custom_audio_details_var.set("") 

        if len(selected_indices) > 2:
            self.selected_custom_video_details_var.set("Error: Too many selected!")
            self.selected_custom_audio_details_var.set("Select only one video and one audio.")
            return

        video_fmt_details = ""
        audio_fmt_details = ""
        
        for i in selected_indices:
            if 0 <= i < len(self.format_data):
                fmt_item = self.format_data[i]
                is_video_only = fmt_item.get('vcodec', 'none').lower() != 'none' and fmt_item.get('acodec', 'none').lower() == 'none'
                is_audio_only = fmt_item.get('vcodec', 'none').lower() == 'none' and fmt_item.get('acodec', 'none').lower() != 'none'
                
                details_str = f"ID: {fmt_item.get('id')}, Ext: {fmt_item.get('ext')}, Res: {fmt_item.get('res')}, FPS: {fmt_item.get('fps')}, Codec: {fmt_item.get('vcodec' if is_video_only else 'acodec')}"

                if is_video_only and not video_fmt_details:
                    video_fmt_details = details_str
                elif is_audio_only and not audio_fmt_details:
                    audio_fmt_details = details_str
                elif is_video_only and video_fmt_details:
                     video_fmt_details = "Multiple videos selected!"
                elif is_audio_only and audio_fmt_details:
                     audio_fmt_details = "Multiple audios selected!"

        self.selected_custom_video_details_var.set(video_fmt_details if video_fmt_details else "Select a video-only format")
        self.selected_custom_audio_details_var.set(audio_fmt_details if audio_fmt_details else "Select an audio-only format")

    def quit_application(self):
        self.root.destroy()

    def update_log(self, message, add_timestamp=False):
        if not message: return 
        try:
            self.log_text.config(state=tk.NORMAL)
            log_entry = ""
            if add_timestamp: 
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"[{timestamp}] "
            log_entry += str(message) 
            self.log_text.insert(tk.END, f"{log_entry}\n")
            self.log_text.see(tk.END) 
            self.log_text.config(state=tk.DISABLED)
        except tk.TclError as e:
            print(f"Error updating log: {e}")

    def clear_log(self):
        try:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete('1.0', tk.END)
            self.log_text.config(state=tk.DISABLED)
            self.update_log("Log cleared.", add_timestamp=True)
        except tk.TclError as e:
            print(f"Error clearing log: {e}")

    def copy_log_to_clipboard(self):
        try:
            log_content = self.log_text.get('1.0', tk.END).strip() 
            if log_content:
                self.root.clipboard_clear()
                self.root.clipboard_append(log_content)
                self.update_log("Log content copied to clipboard.", add_timestamp=True)
            else:
                self.update_log("Log is empty. Nothing to copy.", add_timestamp=True)
        except tk.TclError as e:
            print(f"Error copying log: {e}")

    def _set_ui_state(self, state):
        widgets_to_toggle = [
            self.yt_dlp_path_entry, self.browse_yt_dlp_button, 
            self.ffmpeg_path_entry, self.browse_ffmpeg_button, 
            self.url_entry, self.choose_dir_button, 
            self.fetch_button, self.download_button,
            self.selected_format_radio, self.audio_only_radio, self.custom_merge_radio 
        ]
        for widget in widgets_to_toggle:
            if widget:
                widget.config(state=state)

    def browse_yt_dlp_path(self):
        path = filedialog.askopenfilename(parent=self.root, title="Select yt-dlp Executable")
        if path:
            if os.name != 'nt' and not os.access(path, os.X_OK):
                messagebox.showwarning("Permission Warning", 
                                       f"The selected file '{os.path.basename(path)}' may not be executable. ")
            self.yt_dlp_path_var.set(path)
            self.update_log(f"yt-dlp path set to: {path}")
            self.check_executable_path('yt-dlp', path, self.yt_dlp_status_label, "https://github.com/yt-dlp/yt-dlp#installation")


    def browse_ffmpeg_path(self):
        path = filedialog.askopenfilename(parent=self.root, title="Select ffmpeg Executable")
        if path:
            if os.name != 'nt' and not os.access(path, os.X_OK):
                messagebox.showwarning("Permission Warning",
                                       f"The selected file '{os.path.basename(path)}' may not be executable. ")
            self.ffmpeg_path_var.set(path)
            self.update_log(f"ffmpeg path set to: {path}")
            self.check_executable_path('ffmpeg', path, self.ffmpeg_status_label, "https://ffmpeg.org/download.html")


    def choose_download_dir(self):
        path = filedialog.askdirectory(parent=self.root, title="Select Download Directory")
        if path:
            self.download_dir_var.set(path)
            self.update_log(f"Download directory set to: {path}")

    def _prepare_yt_dlp_command_base(self):
        base_cmd = []
        ffmpeg_path = self.ffmpeg_path_var.get()
        # Only add --ffmpeg-location if a specific path is given AND it's not just the command name "ffmpeg" (which implies PATH usage)
        # A more robust check might be to see if ffmpeg_path contains path separators.
        # For now, if it's not empty and not 'ffmpeg', assume it's a specific path.
        if ffmpeg_path and ffmpeg_path.strip().lower() != 'ffmpeg': 
             if os.path.isfile(ffmpeg_path): 
                base_cmd.extend(['--ffmpeg-location', ffmpeg_path])
             else:
                self.root.after(0, lambda: self.update_log(f"Warning: Custom ffmpeg path '{ffmpeg_path}' is invalid. yt-dlp will try to find ffmpeg in PATH."))
        return base_cmd


    def fetch_formats_async(self):
        yt_dlp_path = self.yt_dlp_path_var.get()
        url = self.url_var.get()

        if not yt_dlp_path: messagebox.showerror("Error", "Please specify the yt-dlp path."); return
        if not os.path.isfile(yt_dlp_path) and not shutil.which(yt_dlp_path) : 
             messagebox.showerror("Error", f"yt-dlp not found at '{yt_dlp_path}' or in PATH."); return
        if os.path.isfile(yt_dlp_path) and os.name != 'nt' and not os.access(yt_dlp_path, os.X_OK): 
            messagebox.showerror("Permission Error", f"yt-dlp not executable: {yt_dlp_path}"); return
        
        if not url: messagebox.showerror("Error", "Please enter a YouTube URL."); return
        
        self._set_ui_state(tk.DISABLED)
        self.video_title = "Untitled Video" 
        self.update_log("Fetching formats using JSON output...", add_timestamp=True)
        self.formats_listbox.delete(0, tk.END) 
        self.format_data = []
        self.on_download_option_change() 

        thread = threading.Thread(target=self._fetch_formats_thread, args=(yt_dlp_path, url))
        thread.daemon = True
        thread.start()

    def _fetch_formats_thread(self, yt_dlp_path, url):
        try:
            yt_dlp_command_options = self._prepare_yt_dlp_command_base()
            command = [yt_dlp_path, url] + yt_dlp_command_options + \
                      ['--no-warnings', '--ignore-config', '--skip-download', '--no-color', '-J']
            
            self.root.after(0, lambda cmd_str=f"Executing command: {' '.join(command)}": self.update_log(cmd_str))
            
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                       text=True, encoding='utf-8', startupinfo=startupinfo)
            stdout, stderr = process.communicate(timeout=60) 

            if stdout: 
                self.root.after(0, lambda: self.update_log("--- yt-dlp stdout (JSON) ---"))
                log_stdout_msg = stdout[:1000] + ("..." if len(stdout) > 1000 else "")
                self.root.after(0, lambda msg=log_stdout_msg: self.update_log(msg))
                self.root.after(0, lambda: self.update_log("--- end yt-dlp stdout ---"))
            if stderr: 
                self.root.after(0, lambda: self.update_log("--- yt-dlp stderr ---"))
                self.root.after(0, lambda msg=stderr: self.update_log(msg))
                self.root.after(0, lambda: self.update_log("--- end yt-dlp stderr ---"))

            if process.returncode == 0 and stdout:
                parsed_formats = []
                try:
                    video_info = json.loads(stdout)
                    self.video_title = video_info.get('title', 'Untitled Video') 
                    formats_json_list = video_info.get('formats', [])
                    self.root.after(0, lambda num_formats=len(formats_json_list): self.update_log(f"Found {num_formats} formats in JSON output."))

                    for fmt_json in formats_json_list:
                        width = fmt_json.get('width')
                        height = fmt_json.get('height')
                        resolution = 'N/A'
                        if width and height: resolution = f"{width}x{height}"
                        elif fmt_json.get('resolution'): resolution = fmt_json.get('resolution')
                        filesize_val = fmt_json.get('filesize_approx', fmt_json.get('filesize'))
                        format_item = {
                            'id': fmt_json.get('format_id', 'N/A'), 'ext': fmt_json.get('ext', 'N/A'),
                            'res': resolution, 'fps': str(fmt_json.get('fps', 'N/A')), 
                            'size': str(filesize_val) if filesize_val is not None else 'N/A', 
                            'note': fmt_json.get('format_note', ''), 
                            'vcodec': fmt_json.get('vcodec', 'none'), 'acodec': fmt_json.get('acodec', 'none'),
                            'protocol': fmt_json.get('protocol', 'N/A')
                        }
                        if format_item['id'] == 'N/A' and format_item['ext'] == 'N/A':
                             self.root.after(0, lambda item=fmt_json: self.update_log(f"Skipping format with missing id/ext: {item}"))
                             continue
                        parsed_formats.append(format_item)
                    
                    self.root.after(0, lambda num_parsed=len(parsed_formats): self.update_log(f"Successfully parsed {num_parsed} formats from JSON."))
                    self.root.after(0, self._update_formats_listbox, parsed_formats) 
                    if not parsed_formats and formats_json_list:
                         self.root.after(0, lambda: self.update_log("Warning: Formats found in JSON, but none mapped. Check parsing."))
                except json.JSONDecodeError as je:
                    self.root.after(0, lambda err=je: self.update_log(f"Failed to parse JSON from yt-dlp: {err}"))
                    self.root.after(0, lambda err=je: messagebox.showerror("JSON Parse Error", f"Could not parse format info: {err}\n\nSee log."))
                    self.root.after(0, self._update_formats_listbox, [])
            elif process.returncode != 0: 
                error_message = f"Fetch Error (yt-dlp code {process.returncode}): {stderr.strip() if stderr else 'Unknown'}"
                if not stderr.strip() and stdout.strip(): error_message += f"\nStdout: {stdout.strip()}" 
                self.root.after(0, lambda err_msg=error_message: messagebox.showerror("Fetch Error", err_msg))
                self.root.after(0, lambda err_msg=error_message: self.update_log(f"Failed to fetch. Details: {err_msg}"))
                self.root.after(0, self._update_formats_listbox, []) 
            elif not stdout: 
                 self.root.after(0, lambda: self.update_log("yt-dlp success but no JSON output."))
                 self.root.after(0, self._update_formats_listbox, [])
        except Exception as e:
            self.root.after(0, lambda err=e: messagebox.showerror("Unexpected Error", f"Fetching error: {type(err).__name__} - {err}"))
            self.root.after(0, lambda err=e: self.update_log(f"Fetch error: {type(err).__name__} - {err}"))
        finally:
            self.root.after(0, self._set_ui_state, tk.NORMAL)

    def _update_formats_listbox(self, formats):
        self.update_log(f"Updating listbox with {len(formats)} formats.") 
        self.formats_listbox.delete(0, tk.END)
        self.format_data = formats 
        if not formats: 
             self.formats_listbox.insert(tk.END, "No formats to display.") 
             self.update_log("Formats list empty, displayed 'No formats to display'.")
             return 

        for i, fmt in enumerate(formats):
            res_display = fmt.get('res', 'N/A') 
            vcodec = fmt.get('vcodec', 'none').lower()
            acodec = fmt.get('acodec', 'none').lower()
            if vcodec != 'none' and vcodec != 'unknown_video': 
                if acodec == 'none' or acodec == 'unknown_audio': 
                    res_display += " (Video Only)"
            elif acodec != 'none' and acodec != 'unknown_audio': 
                res_display = "Audio Only"
            elif vcodec == 'none' and acodec == 'none': 
                res_display = "Metadata/Unknown"
            
            fps_display = f"{fmt.get('fps','N/A')}fps" if fmt.get('fps','N/A') not in ['N/A', '0', None] else "" 
            note_display = fmt.get('note', '')
            if not note_display or note_display == 'N/A':
                note_parts = []
                if vcodec != 'none' and vcodec != 'unknown_video': note_parts.append(f"v: {fmt.get('vcodec')}")
                if acodec != 'none' and acodec != 'unknown_audio': note_parts.append(f"a: {fmt.get('acodec')}")
                note_display = ", ".join(note_parts) if note_parts else ""
            else: 
                codec_info_str = ""
                v_str = f"v: {fmt.get('vcodec')}" if fmt.get('vcodec') not in ['none', 'unknown_video', None] else ""
                a_str = f"a: {fmt.get('acodec')}" if fmt.get('acodec') not in ['none', 'unknown_audio', None] else ""
                if v_str and a_str: codec_info_str = f" ({v_str}, {a_str})"
                elif v_str: codec_info_str = f" ({v_str})"
                elif a_str: codec_info_str = f" ({a_str})"
                if codec_info_str and codec_info_str not in note_display: note_display += codec_info_str
            list_entry = (f"ID: {fmt.get('id','N/A'):<5} | Ext: {fmt.get('ext','N/A'):<5} | "
                          f"Res: {res_display:<22} | {fps_display:<7} | " 
                          f"Size: {fmt.get('size','N/A'):<12} | Note: {note_display}")
            self.formats_listbox.insert(tk.END, list_entry)
        self.update_log("Finished updating listbox.")
        self.on_format_selection_change() 

    def download_async(self):
        yt_dlp_path = self.yt_dlp_path_var.get()
        url = self.url_var.get()
        download_dir_path = self.download_dir_var.get() 
        download_mode = self.download_option_var.get()

        # --- Validate yt-dlp path ---
        yt_dlp_valid = False
        if os.path.isfile(yt_dlp_path):
            if os.name == 'nt' or os.access(yt_dlp_path, os.X_OK):
                yt_dlp_valid = True
        if not yt_dlp_valid:
            yt_dlp_in_path = shutil.which(yt_dlp_path)
            if yt_dlp_in_path and (os.name == 'nt' or os.access(yt_dlp_in_path, os.X_OK)):
                yt_dlp_path = yt_dlp_in_path # Use full path from PATH
                yt_dlp_valid = True
        if not yt_dlp_valid:
            messagebox.showerror("Error", f"yt-dlp not found or not executable at '{self.yt_dlp_path_var.get()}' or in PATH."); return
        
        if not url: messagebox.showerror("Error", "Enter YouTube URL."); return
        if not download_dir_path or not os.path.isdir(download_dir_path): 
            messagebox.showerror("Error", "Select valid download directory."); return

        selected_indices = self.formats_listbox.curselection()
        full_output_path = None 
        custom_dl_params = None 
        format_codes_to_download = [] 

        if download_mode == "selected":
            if not selected_indices:
                messagebox.showwarning("Selection Warning", "No formats selected for download."); return
            if len(selected_indices) == 1:
                if 0 <= selected_indices[0] < len(self.format_data):
                    fmt = self.format_data[selected_indices[0]]
                    default_filename = f"{self.video_title or 'Selected_Format'}_{fmt.get('id','fmt')}.{fmt.get('ext','bin')}"
                    filetypes = [(f"{fmt.get('ext','').upper()} files", f"*.{fmt.get('ext','*')}"), ("All files", "*.*")]
                    full_output_path = filedialog.asksaveasfilename(parent=self.root, initialdir=download_dir_path, initialfile=default_filename, defaultextension=f".{fmt.get('ext','bin')}", filetypes=filetypes)
                    if not full_output_path: return 
                    format_codes_to_download = [fmt['id']]
            else: 
                format_codes_to_download = [self.format_data[i]['id'] for i in selected_indices if 0 <= i < len(self.format_data)]

        elif download_mode == "custom_merge_mp4":
            if len(selected_indices) != 2:
                messagebox.showwarning("Selection Error", "For custom merge, select ONE video-only AND ONE audio-only format.")
                return
            selected_fmts_data = [self.format_data[i] for i in selected_indices]
            video_fmt, audio_fmt = None, None
            for fmt_item in selected_fmts_data:
                is_video_only = fmt_item.get('vcodec', 'none').lower() != 'none' and fmt_item.get('acodec', 'none').lower() == 'none'
                is_audio_only = fmt_item.get('vcodec', 'none').lower() == 'none' and fmt_item.get('acodec', 'none').lower() != 'none'
                if is_video_only and not video_fmt: video_fmt = fmt_item
                elif is_audio_only and not audio_fmt: audio_fmt = fmt_item
            if not (video_fmt and audio_fmt):
                messagebox.showwarning("Selection Error", "Invalid selection. Select ONE video-only AND ONE audio-only format.")
                return
            custom_dl_params = {'video_id': video_fmt['id'], 'audio_id': audio_fmt['id']}
            default_filename = f"{self.video_title or 'Custom_Merge'}.mp4"
            full_output_path = filedialog.asksaveasfilename(parent=self.root, initialdir=download_dir_path, initialfile=default_filename, defaultextension=".mp4", filetypes=[("MP4 video", "*.mp4"), ("All files", "*.*")])
            if not full_output_path: return 

        elif download_mode == "audio_mp3":
            default_filename = f"{self.video_title or 'Audio_Download'}.mp3"
            full_output_path = filedialog.asksaveasfilename(parent=self.root, initialdir=download_dir_path, initialfile=default_filename, defaultextension=".mp3", filetypes=[("MP3 audio", "*.mp3"), ("All files", "*.*")])
            if not full_output_path: return 

        self._set_ui_state(tk.DISABLED)
        self.update_log("Starting download...", add_timestamp=True)
        
        dl_args = custom_dl_params if download_mode == "custom_merge_mp4" else format_codes_to_download
        output_location = full_output_path if full_output_path else download_dir_path

        thread = threading.Thread(target=self._download_thread, 
                                  args=(yt_dlp_path, url, output_location, download_mode, dl_args))
        thread.daemon = True
        thread.start()

    def _download_thread(self, yt_dlp_path, url, output_target, download_mode, dl_params):
        try:
            yt_dlp_command_options = self._prepare_yt_dlp_command_base()
            base_command = [yt_dlp_path, url] + yt_dlp_command_options
            common_dl_options = ['--no-warnings', '--ignore-config', '--no-color']

            startupinfo = None
            if os.name == 'nt': 
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            command = [] 
            process_dl_message = "" 

            if download_mode == "audio_mp3":
                process_dl_message = "Downloading audio as MP3..."
                command = base_command + ['-x', '--audio-format', 'mp3'] + common_dl_options + ['-o', output_target] 
            
            elif download_mode == "custom_merge_mp4":
                video_id = dl_params['video_id']
                audio_id = dl_params['audio_id']
                process_dl_message = f"Downloading video ({video_id}) and audio ({audio_id}) for MP4 merge..."
                self.root.after(0, lambda: self.update_log("Note: This merge may require ffmpeg.", add_timestamp=False))
                format_selection_str = f"{video_id}+{audio_id}"
                command = base_command + ['-f', format_selection_str, '--merge-output-format', 'mp4'] + common_dl_options + ['-o', output_target] 

            elif download_mode == "selected":
                pass 
            
            if download_mode == "audio_mp3" or download_mode == "custom_merge_mp4":
                self.root.after(0, lambda msg=process_dl_message: self.update_log(msg))
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', startupinfo=startupinfo)
                for line in iter(process.stdout.readline, ''):
                    if line: self.root.after(0, lambda msg=line.strip(): self.update_log(msg))
                process.stdout.close()
                return_code = process.wait()
                
                dl_type_msg = "Audio (MP3)" if download_mode == "audio_mp3" else "Custom Merged MP4"
                if return_code == 0:
                    self.root.after(0, lambda: self.update_log(f"{dl_type_msg} download complete.", add_timestamp=True))
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"{dl_type_msg} download completed successfully!"))
                else:
                    self.root.after(0, lambda rc=return_code: self.update_log(f"{dl_type_msg} download failed (code {rc}).", add_timestamp=True))
                    self.root.after(0, lambda rc=return_code: messagebox.showerror("Download Error", f"{dl_type_msg} download failed. Exit code: {rc}. Check log."))

            elif download_mode == "selected":
                format_codes = dl_params 
                total_formats = len(format_codes)
                success_count = 0
                if not format_codes: self.root.after(0, lambda: self.update_log("No valid format codes to download."))
                
                for i, f_code in enumerate(format_codes):
                    self.root.after(0, lambda code=f_code, idx=i, total=total_formats: self.update_log(f"Downloading format {code} ({idx+1}/{total})..."))
                    
                    current_output_option = ['-o']
                    # If output_target is a directory (multi-select case where no specific file was chosen for all)
                    # OR if it's a single download but somehow output_target wasn't a full path (fallback, less likely with current logic)
                    if (os.path.isdir(output_target) and len(format_codes) > 1) or \
                       (len(format_codes) == 1 and not os.path.isabs(os.path.dirname(output_target))): # Check if output_target looks like just a filename for single download
                        current_output_option.append(os.path.join(str(output_target), '%(title)s [%(format_id)s].%(ext)s'))
                    else: # Single select case with specific full path or custom/audio modes
                        current_output_option.append(output_target)


                    current_command = base_command + ['-f', f_code] + common_dl_options + current_output_option

                    process = subprocess.Popen(current_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', startupinfo=startupinfo)
                    for line in iter(process.stdout.readline, ''):
                        if line: self.root.after(0, lambda msg=line.strip(): self.update_log(msg))
                    process.stdout.close()
                    return_code = process.wait()
                    if return_code == 0:
                        success_count +=1
                        self.root.after(0, lambda code=f_code: self.update_log(f"Format {code} downloaded successfully."))
                    else:
                        self.root.after(0, lambda code=f_code, rc=return_code: self.update_log(f"Failed to download format {code} (code {rc})."))
                
                final_message = f"{success_count}/{total_formats} selected format(s) downloaded."
                self.root.after(0, lambda msg=final_message: self.update_log(msg, add_timestamp=True))
                if total_formats == 0 and not format_codes: self.root.after(0, lambda: self.update_log("No formats selected."))
                elif success_count == total_formats and total_formats > 0: 
                    self.root.after(0, lambda: messagebox.showinfo("Success", "All selected formats downloaded!"))
                elif success_count > 0:
                     self.root.after(0, lambda msg=final_message: messagebox.showwarning("Partial Success", f"{msg} Check log."))
                elif total_formats > 0 : 
                     self.root.after(0, lambda: messagebox.showerror("Download Failed", "None selected could be downloaded. Check log."))
            
        except Exception as e: 
            self.root.after(0, lambda err=e: messagebox.showerror("Unexpected Error", f"Download error: {type(err).__name__} - {err}"))
            self.root.after(0, lambda err=e: self.update_log(f"Download error: {type(err).__name__} - {err}", add_timestamp=True))
        finally:
            self.root.after(0, self._set_ui_state, tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = YTDLP_GUI(root)
    root.protocol("WM_DELETE_WINDOW", app.quit_application) 
    root.mainloop()

