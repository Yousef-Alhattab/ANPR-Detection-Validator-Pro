import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from PIL import Image, ImageTk
import os
from pathlib import Path
import json

class ANPRValidator:
    def __init__(self, root):
        self.root = root
        self.root.title("ANPR Detection Validator Pro")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f2f5')
        
        # Data variables
        self.df = None
        self.current_index = 0
        self.image_path = ""
        self.validation_results = {}
        
        # NEW: Validation CSV tracking
        self.validation_df = None
        self.csv_output_path = ""
        
        # Image variables
        self.front_image = None
        self.rear_image = None
        self.front_photo = None
        self.rear_photo = None
        self.front_image_path = None
        self.rear_image_path = None
        
        # NEW: In-place zoom variables
        self.front_zoom_level = 1.0
        self.rear_zoom_level = 1.0
        self.front_pan_x = 0
        self.front_pan_y = 0
        self.rear_pan_x = 0
        self.rear_pan_y = 0
        self.front_dragging = False
        self.rear_dragging = False
        
        # Create GUI
        self.create_widgets()
        self.create_styles()
        
    def create_styles(self):
        """Create custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 24, 'bold'), background='#f0f2f5', foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#f0f2f5', foreground='#34495e')
        style.configure('Info.TLabel', font=('Arial', 10), background='#f0f2f5', foreground='#7f8c8d')
        style.configure('Success.TButton', font=('Arial', 9, 'bold'))
        style.configure('Error.TButton', font=('Arial', 9, 'bold'))
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Control panel
        self.create_control_panel()
        
        # Navigation panel
        self.create_navigation_panel()
        
        # Main content area
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
        
    def create_control_panel(self):
        """Create the control panel with file selection and settings"""
        control_frame = tk.LabelFrame(self.root, text="📁 File & Path Settings", font=('Arial', 12, 'bold'), 
                                    bg='#ecf0f1', relief='groove', bd=2)
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # CSV file selection
        csv_frame = tk.Frame(control_frame, bg='#ecf0f1')
        csv_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(csv_frame, text="CSV File:", style='Header.TLabel').pack(side='left')
        self.csv_path_var = tk.StringVar()
        csv_entry = ttk.Entry(csv_frame, textvariable=self.csv_path_var, width=60)
        csv_entry.pack(side='left', padx=10, fill='x', expand=True)
        
        ttk.Button(csv_frame, text="Browse CSV", command=self.browse_csv).pack(side='right', padx=5)
        
        # Images path selection
        img_frame = tk.Frame(control_frame, bg='#ecf0f1')
        img_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(img_frame, text="Images Path:", style='Header.TLabel').pack(side='left')
        self.img_path_var = tk.StringVar()
        img_entry = ttk.Entry(img_frame, textvariable=self.img_path_var, width=60)
        img_entry.pack(side='left', padx=10, fill='x', expand=True)
        
        ttk.Button(img_frame, text="Browse Folder", command=self.browse_images).pack(side='right', padx=5)
        
    def create_navigation_panel(self):
        """Create navigation controls"""
        nav_frame = tk.Frame(self.root, bg='#3498db', height=60)
        nav_frame.pack(fill='x', padx=20, pady=5)
        nav_frame.pack_propagate(False)
        
        # Navigation buttons
        btn_frame = tk.Frame(nav_frame, bg='#3498db')
        btn_frame.pack(side='left', fill='y', pady=10)
        
        self.prev_btn = tk.Button(btn_frame, text="◀ Previous", font=('Arial', 11, 'bold'), 
                                bg='#2980b9', fg='white', command=self.previous_record)
        self.prev_btn.pack(side='left', padx=5)
        
        self.next_btn = tk.Button(btn_frame, text="Next ▶", font=('Arial', 11, 'bold'), 
                                bg='#2980b9', fg='white', command=self.next_record)
        self.next_btn.pack(side='left', padx=5)
        
        # Current record info
        info_frame = tk.Frame(nav_frame, bg='#3498db')
        info_frame.pack(side='right', fill='y', pady=10)
        
        self.record_info = tk.Label(info_frame, text="No data loaded", font=('Arial', 12, 'bold'), 
                                  bg='#3498db', fg='white')
        self.record_info.pack(side='right', padx=10)
        
        # Progress bar
        progress_frame = tk.Frame(nav_frame, bg='#3498db')
        progress_frame.pack(fill='x', pady=15, padx=100)
        
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, style='success.Horizontal.TProgressbar')
        self.progress_bar.pack(fill='x')
        
    def create_main_content(self):
        """Create the main content area with image viewers"""
        content_frame = tk.Frame(self.root, bg='#f0f2f5')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left side - Front plate
        self.create_image_panel(content_frame, "left", "🚘 Front Plate Detection")
        
        # Right side - Rear plate  
        self.create_image_panel(content_frame, "right", "🚗 Rear Plate Detection")
        
    def create_image_panel(self, parent, side, title):
        """Create an image panel for front or rear plate"""
        panel_frame = tk.LabelFrame(parent, text=title, font=('Arial', 14, 'bold'), 
                                  bg='white', relief='groove', bd=2)
        panel_frame.pack(side=side, fill='both', expand=True, padx=10)
        
        # Detection result display
        result_frame = tk.Frame(panel_frame, bg='white', height=60)
        result_frame.pack(fill='x', padx=10, pady=5)
        result_frame.pack_propagate(False)
        
        prefix = 'front' if 'Front' in title else 'rear'
        
        # Detected plate number
        setattr(self, f'{prefix}_detected_var', tk.StringVar())
        detected_label = tk.Label(result_frame, text="Detected:", font=('Arial', 11, 'bold'), bg='white')
        detected_label.pack(side='left', pady=10)
        
        detected_display = tk.Label(result_frame, textvariable=getattr(self, f'{prefix}_detected_var'), 
                                  font=('Courier', 14, 'bold'), bg='#ecf0f1', relief='sunken', 
                                  bd=2, padx=10, pady=5)
        detected_display.pack(side='left', padx=10, pady=10)
        
        # Validation buttons
        validation_frame = tk.Frame(result_frame, bg='white')
        validation_frame.pack(side='right', pady=10)
        
        correct_btn = tk.Button(validation_frame, text="✓ Correct", font=('Arial', 10, 'bold'), 
                              bg='#27ae60', fg='white', width=10,
                              command=lambda: self.mark_validation(prefix, True))
        correct_btn.pack(side='right', padx=2)
        
        incorrect_btn = tk.Button(validation_frame, text="✗ Wrong", font=('Arial', 10, 'bold'), 
                                bg='#e74c3c', fg='white', width=10,
                                command=lambda: self.mark_validation(prefix, False))
        incorrect_btn.pack(side='right', padx=2)
        
        # Image display area
        img_frame = tk.Frame(panel_frame, bg='#ecf0f1', relief='sunken', bd=2)
        img_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # ZOOM CONTROLS - Always visible
        zoom_frame = tk.Frame(img_frame, bg='#ecf0f1')
        zoom_frame.pack(fill='x', padx=5, pady=2)
        
        tk.Button(zoom_frame, text="🔍+ Zoom In", 
                command=lambda: self.zoom_in_place(prefix),
                bg='#3498db', fg='white', font=('Arial', 10, 'bold'), width=12).pack(side='left', padx=2)
        tk.Button(zoom_frame, text="🔍- Zoom Out", 
                command=lambda: self.zoom_out_place(prefix),
                bg='#3498db', fg='white', font=('Arial', 10, 'bold'), width=12).pack(side='left', padx=2)
        tk.Button(zoom_frame, text="↺ Reset View", 
                command=lambda: self.reset_zoom_place(prefix),
                bg='#e67e22', fg='white', font=('Arial', 10, 'bold'), width=12).pack(side='left', padx=2)
        
        # Current zoom level display
        zoom_info = tk.Label(zoom_frame, text="", font=('Arial', 9), bg='#ecf0f1', fg='#7f8c8d')
        zoom_info.pack(side='right', padx=10)
        setattr(self, f'{prefix}_zoom_info', zoom_info)
        
        # Instructions for click to zoom
        instruction_frame = tk.Frame(img_frame, bg='#ecf0f1')
        instruction_frame.pack(fill='x', padx=5, pady=2)
        
        instruction_label = tk.Label(instruction_frame, text="💡 Click on image to zoom that area | Drag to pan around", 
                                   font=('Arial', 9), bg='#ecf0f1', fg='#7f8c8d')
        instruction_label.pack(side='left')
        
        # Image canvas with hand cursor
        canvas = tk.Canvas(img_frame, bg='white', relief='sunken', bd=1, cursor='crosshair')
        canvas.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Bind events for in-place zoom and pan - SIMPLE bindings
        canvas.bind("<Button-1>", lambda e: self.on_image_click_zoom(e, prefix))
        canvas.bind("<B1-Motion>", lambda e: self.on_image_drag(e, prefix))  
        canvas.bind("<ButtonRelease-1>", lambda e: self.on_drag_end(e, prefix))
        canvas.bind("<MouseWheel>", lambda e: self.on_mouse_wheel(e, prefix))
        
        # Change cursor when dragging
        canvas.bind("<Enter>", lambda e: canvas.configure(cursor="hand2"))
        canvas.bind("<Leave>", lambda e: canvas.configure(cursor="crosshair"))
        
        setattr(self, f'{prefix}_canvas', canvas)
        
        # File name display
        setattr(self, f'{prefix}_filename_var', tk.StringVar())
        filename_label = tk.Label(panel_frame, textvariable=getattr(self, f'{prefix}_filename_var'), 
                                font=('Arial', 9), bg='white', fg='#7f8c8d')
        filename_label.pack(fill='x', padx=10, pady=2)
        
    def create_status_bar(self):
        """Create status bar at the bottom"""
        status_frame = tk.Frame(self.root, bg='#34495e', height=30)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Load CSV file and set images path to begin")
        status_label = tk.Label(status_frame, textvariable=self.status_var, 
                              bg='#34495e', fg='white', font=('Arial', 10))
        status_label.pack(side='left', padx=10, pady=5)
        
        # Validation stats
        self.stats_var = tk.StringVar()
        stats_label = tk.Label(status_frame, textvariable=self.stats_var, 
                             bg='#34495e', fg='#ecf0f1', font=('Arial', 10))
        stats_label.pack(side='right', padx=10, pady=5)
        
    def browse_csv(self):
        """Browse and select CSV file"""
        filename = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.csv_path_var.set(filename)
            self.load_csv()
            
    def browse_images(self):
        """Browse and select images folder"""
        folder = filedialog.askdirectory(title="Select Images Folder")
        if folder:
            self.img_path_var.set(folder)
            self.image_path = folder
            self.validate_image_path()
            self.update_display()
            
    def validate_image_path(self):
        """Validate that the image path contains some image files"""
        if not self.image_path or not os.path.exists(self.image_path):
            return
            
        # Count image files in the directory
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        image_count = 0
        
        try:
            for file in os.listdir(self.image_path):
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_count += 1
                    
            if image_count > 0:
                self.status_var.set(f"Found {image_count} image files in selected folder")
            else:
                self.status_var.set("⚠️ No image files found in selected folder")
                messagebox.showwarning("Warning", 
                                     f"No image files found in:\n{self.image_path}\n\n" +
                                     "Please select the correct folder containing your .jpg/.png images.")
        except Exception as e:
            self.status_var.set(f"Error accessing folder: {str(e)}")
            
    def load_csv(self):
        """Load CSV file and initialize data"""
        try:
            csv_path = self.csv_path_var.get()
            if not csv_path:
                return
                
            self.df = pd.read_csv(csv_path)
            
            # Validate required columns
            required_cols = ['vdata_id', 'fr_anpr', 're_anpr', 'fr_mediaid', 're_mediaid']
            missing_cols = [col for col in required_cols if col not in self.df.columns]
            
            if missing_cols:
                messagebox.showerror("Error", f"Missing columns: {', '.join(missing_cols)}")
                return
            
            # CREATE VALIDATION CSV with new columns
            self.create_validation_csv(csv_path)
                
            self.current_index = 0
            self.validation_results = {}
            self.update_navigation()
            self.update_display()
            
            self.status_var.set(f"Loaded {len(self.df)} records from CSV - Empty validation CSV created!")
            messagebox.showinfo("Success", f"Successfully loaded {len(self.df)} records!\n\n"
                              f"Empty validation CSV created: {self.csv_output_path}\n"
                              f"Records will be added only when you validate them!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
    
    def create_validation_csv(self, original_csv_path):
        """Create EMPTY validation CSV - only add rows when validated"""
        try:
            # Create EMPTY dataframe with same columns as original + validation columns
            columns = list(self.df.columns) + ['fr_validation', 're_validation']
            self.validation_df = pd.DataFrame(columns=columns)
            
            # Create output filename
            csv_name = os.path.splitext(os.path.basename(original_csv_path))[0]
            csv_dir = os.path.dirname(original_csv_path)
            self.csv_output_path = os.path.join(csv_dir, f"{csv_name}_VALIDATED.csv")
            
            # Save EMPTY CSV with just headers
            self.validation_df.to_csv(self.csv_output_path, index=False)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create validation CSV: {str(e)}")
    
    def add_validated_record(self, prefix, validation_status):
        """Add current record to validation CSV when validated"""
        try:
            if self.validation_df is None or self.df is None:
                return
            
            current_row = self.df.iloc[self.current_index].copy()
            
            # Check if this record is already in validation CSV
            existing_record = self.validation_df[
                self.validation_df['vdata_id'] == current_row['vdata_id']
            ]
            
            if len(existing_record) == 0:
                # NEW RECORD - Add it to validation CSV
                new_row = current_row.to_dict()
                new_row['fr_validation'] = ''  # Empty initially
                new_row['re_validation'] = ''  # Empty initially
                
                # Add the row
                new_df_row = pd.DataFrame([new_row])
                self.validation_df = pd.concat([self.validation_df, new_df_row], ignore_index=True)
            
            # Update the validation status for the correct column
            column_name = 'fr_validation' if prefix == 'front' else 're_validation'
            self.validation_df.loc[
                self.validation_df['vdata_id'] == current_row['vdata_id'], 
                column_name
            ] = validation_status
            
            # Save updated CSV
            self.validation_df.to_csv(self.csv_output_path, index=False)
            
            # Update status with record count
            total_validated = len(self.validation_df)
            self.status_var.set(f"✅ {validation_status} recorded! Total validated records: {total_validated}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update validation CSV: {str(e)}")
    
    def show_error_options(self, prefix):
        """Show error selection popup - BIGGER with separate Hidden/Broken"""
        # Create popup window - BIGGER SIZE!
        error_popup = tk.Toplevel(self.root)
        error_popup.title(f"🔍 {prefix.title()} Plate - Select Error Type")
        error_popup.geometry("600x500")  # BIGGER!
        error_popup.configure(bg='#2c3e50')
        error_popup.resizable(False, False)
        
        # Make it modal
        error_popup.transient(self.root)
        error_popup.grab_set()
        
        # Center on screen
        error_popup.geometry(f"600x500+{(error_popup.winfo_screenwidth()//2)-300}+{(error_popup.winfo_screenheight()//2)-250}")
        
        # Main frame
        main_frame = tk.Frame(error_popup, bg='#2c3e50', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text=f"❌ {prefix.upper()} PLATE ERROR TYPE", 
                              font=('Arial', 16, 'bold'), bg='#2c3e50', fg='#e74c3c')
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = tk.Label(main_frame, text="Select the specific error type:", 
                                 font=('Arial', 11), bg='#2c3e50', fg='#ecf0f1')
        subtitle_label.pack(pady=(0, 15))
        
        # Error options - SEPARATED Hidden and Broken!
        error_options = [
            ("🙈 Hidden", "hidden"),
            ("💥 Broken", "broken"),
            ("❌ Fail", "fail"),
            ("🚗 No License Plate", "no_LP"),
            ("🚙 No Vehicle", "no_vehicle"),
            ("🌫️ Blur", "blur"),
            ("🏍️ Motorcycle", "moto"),
            ("🔄 Wrong Pair", "wrong_pair")
        ]
        
        # Create buttons in a grid - 2 columns, 4 rows
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill='both', expand=True, pady=10)
        
        for i, (display_name, error_code) in enumerate(error_options):
            btn = tk.Button(button_frame, 
                           text=display_name,
                           font=('Arial', 12, 'bold'),
                           bg='#e74c3c', fg='white',
                           width=22, height=2,  # BIGGER buttons!
                           relief='raised', bd=3,
                           command=lambda code=error_code: self.select_error(error_popup, prefix, code))
            
            row = i // 2
            col = i % 2
            btn.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
        
        # Configure grid weights for even spacing
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Cancel button
        cancel_frame = tk.Frame(main_frame, bg='#2c3e50')
        cancel_frame.pack(fill='x', pady=(20, 0))
        
        cancel_btn = tk.Button(cancel_frame, text="❌ CANCEL", 
                              font=('Arial', 12, 'bold'),
                              bg='#95a5a6', fg='white',
                              width=15, height=2,
                              command=error_popup.destroy)
        cancel_btn.pack(side='right')
        
        # Instructions
        instruction_label = tk.Label(main_frame, 
                                   text="💡 Click on the error type that best describes the issue",
                                   font=('Arial', 9), bg='#2c3e50', fg='#bdc3c7')
        instruction_label.pack(side='bottom', pady=(10, 0))
        
        # Focus and bind ESC
        error_popup.bind("<Escape>", lambda e: error_popup.destroy())
        error_popup.focus_set()
    
    def select_error(self, popup, prefix, error_code):
        """Handle error selection"""
        # Add/Update record in CSV with error code
        self.add_validated_record(prefix, error_code)
        
        # Update validation results for statistics
        key = f"{self.current_index}_{prefix}"
        self.validation_results[key] = False  # Mark as incorrect
        self.update_validation_stats()
        
        # Close popup
        popup.destroy()
        
        # NO MORE ANNOYING CONFIRMATION POPUP - Just update status bar!
        error_display = error_code.replace('_', ' ').title()
        total_validated = len(self.validation_df)
        self.status_var.set(f"❌ {error_display} recorded for {prefix} plate | Total validated: {total_validated}")
        
        # Check if both plates are validated for auto-advance
        front_key = f"{self.current_index}_front"
        rear_key = f"{self.current_index}_rear"
        
        if front_key in self.validation_results and rear_key in self.validation_results:
            self.root.after(500, self.next_record)  # FASTER auto-advance - no delay for popup
            
    def update_navigation(self):
        """Update navigation buttons and progress"""
        if self.df is None:
            return
            
        total = len(self.df)
        current = self.current_index + 1
        
        self.record_info.config(text=f"Record {current} of {total}")
        self.progress_var.set(int((current / total) * 100))
        
        self.prev_btn.config(state='normal' if self.current_index > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_index < total - 1 else 'disabled')
        
        self.update_validation_stats()
        
    def update_validation_stats(self):
        """Update validation statistics"""
        if not self.validation_results:
            self.stats_var.set("")
            return
            
        total = len(self.validation_results)
        correct = sum(1 for v in self.validation_results.values() if v)
        incorrect = total - correct
        
        self.stats_var.set(f"Validated: {total} | Correct: {correct} | Wrong: {incorrect}")
        
    def update_display(self):
        """Update the display with current record data"""
        if self.df is None or self.current_index >= len(self.df):
            return
            
        current_row = self.df.iloc[self.current_index]
        
        # Update detected plate numbers
        self.front_detected_var.set(current_row.get('fr_anpr', 'N/A'))
        self.rear_detected_var.set(current_row.get('re_anpr', 'N/A'))
        
        # Update filenames
        self.front_filename_var.set(f"File: {current_row.get('fr_mediaid', 'N/A')}")
        self.rear_filename_var.set(f"File: {current_row.get('re_mediaid', 'N/A')}")
        
        # Load and display images
        self.load_images(current_row)
        
        self.status_var.set(f"Viewing record {self.current_index + 1} - ID: {current_row.get('vdata_id', 'N/A')}")
        
    def load_images(self, row):
        """Load and display front and rear images"""
        self.load_image('front', row.get('fr_mediaid', ''))
        self.load_image('rear', row.get('re_mediaid', ''))
        
    def load_image(self, prefix, filename):
        """Load a single image"""
        canvas = getattr(self, f'{prefix}_canvas')
        canvas.delete("all")
        
        # Reset zoom and pan for new image
        setattr(self, f'{prefix}_zoom_level', 1.0)
        setattr(self, f'{prefix}_pan_x', 0)
        setattr(self, f'{prefix}_pan_y', 0)
        
        if not filename or not self.image_path:
            canvas.create_text(canvas.winfo_width()//2, canvas.winfo_height()//2, 
                             text="No image\nor path not set", 
                             font=('Arial', 14), fill='gray')
            self.update_zoom_info(prefix)
            return
        
        # Try different file extensions and paths
        possible_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '']
        possible_paths = []
        
        # Add original filename as-is
        for ext in possible_extensions:
            if filename.endswith(ext) or ext == '':
                test_filename = filename if ext == '' else filename + ext
                possible_paths.append(os.path.join(self.image_path, test_filename))
        
        # Also try removing common suffixes and adding extensions
        base_filename = filename.replace('.NaN', '').replace('.nan', '')
        for ext in ['.jpg', '.jpeg', '.png']:
            possible_paths.append(os.path.join(self.image_path, base_filename + ext))
        
        # Try looking for files that END with the CSV filename
        if filename and self.image_path:
            try:
                for file in os.listdir(self.image_path):
                    if file.endswith(filename + '.jpg') or file.endswith(filename):
                        possible_paths.append(os.path.join(self.image_path, file))
            except:
                pass
            
        image_path = None
        for path in possible_paths:
            if os.path.exists(path):
                image_path = path
                break
        
        try:
            if image_path and os.path.exists(image_path):
                # Store the image path and load original image
                setattr(self, f'{prefix}_image_path', image_path)
                img = Image.open(image_path)
                setattr(self, f'{prefix}_image', img)  # Store original image
                
                # Display the image
                self.update_image_display(prefix)
                
            else:
                canvas.create_text(canvas.winfo_width()//2, canvas.winfo_height()//2, 
                                 text=f"Image not found:\n{filename}", 
                                 font=('Arial', 12), fill='red')
                                 
        except Exception as e:
            canvas.create_text(canvas.winfo_width()//2, canvas.winfo_height()//2, 
                             text=f"Error loading image:\n{str(e)}", 
                             font=('Arial', 10), fill='red')
        
        self.update_zoom_info(prefix)

    def load_image(self, prefix, filename):
        """Load a single image - BACK TO SIMPLE VERSION"""
        canvas = getattr(self, f'{prefix}_canvas')
        canvas.delete("all")
        
        # Reset zoom and pan for new image
        setattr(self, f'{prefix}_zoom_level', 1.0)
        setattr(self, f'{prefix}_pan_x', 0)
        setattr(self, f'{prefix}_pan_y', 0)
        
        if not filename or not self.image_path:
            canvas.create_text(canvas.winfo_width()//2, canvas.winfo_height()//2, 
                             text="No image\nor path not set", 
                             font=('Arial', 14), fill='gray')
            self.update_zoom_info(prefix)
            return
        
        # Try different file extensions and paths
        possible_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '']
        possible_paths = []
        
        # Add original filename as-is
        for ext in possible_extensions:
            if filename.endswith(ext) or ext == '':
                test_filename = filename if ext == '' else filename + ext
                possible_paths.append(os.path.join(self.image_path, test_filename))
        
        # Also try removing common suffixes and adding extensions
        base_filename = filename.replace('.NaN', '').replace('.nan', '')
        for ext in ['.jpg', '.jpeg', '.png']:
            possible_paths.append(os.path.join(self.image_path, base_filename + ext))
        
        # Try looking for files that END with the CSV filename
        if filename and self.image_path:
            try:
                for file in os.listdir(self.image_path):
                    if file.endswith(filename + '.jpg') or file.endswith(filename):
                        possible_paths.append(os.path.join(self.image_path, file))
            except:
                pass
            
        image_path = None
        for path in possible_paths:
            if os.path.exists(path):
                image_path = path
                break
        
        try:
            if image_path and os.path.exists(image_path):
                # Store the image path and original image - SIMPLE!
                setattr(self, f'{prefix}_image_path', image_path)
                img = Image.open(image_path)
                setattr(self, f'{prefix}_image', img)  # Store original image
                
                # Calculate display size while maintaining aspect ratio - BACK TO WORKING VERSION!
                canvas_width = canvas.winfo_width() or 400
                canvas_height = canvas.winfo_height() or 300
                
                img_width, img_height = img.size
                
                # Scale to fit canvas
                scale_x = (canvas_width - 20) / img_width
                scale_y = (canvas_height - 20) / img_height
                scale = min(scale_x, scale_y)
                
                setattr(self, f'{prefix}_scale', scale)  # Store scale for click calculations
                
                # Display normally first
                self.display_image_normal(prefix)
                
            else:
                canvas.create_text(canvas.winfo_width()//2, canvas.winfo_height()//2, 
                                 text=f"Image not found:\n{filename}", 
                                 font=('Arial', 12), fill='red')
                                 
        except Exception as e:
            canvas.create_text(canvas.winfo_width()//2, canvas.winfo_height()//2, 
                             text=f"Error loading image:\n{str(e)}", 
                             font=('Arial', 10), fill='red')
        
        self.update_zoom_info(prefix)

    def display_image_normal(self, prefix):
        """Display image normally - fit to canvas"""
        canvas = getattr(self, f'{prefix}_canvas')
        original_image = getattr(self, f'{prefix}_image', None)
        scale = getattr(self, f'{prefix}_scale', 1)
        
        if not original_image:
            return
            
        canvas.delete("all")
        
        # Get canvas size
        canvas_width = canvas.winfo_width() or 400
        canvas_height = canvas.winfo_height() or 300
        
        # Normal display - fit to canvas
        img_width, img_height = original_image.size
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        img_resized = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img_resized)
        
        # Store reference
        setattr(self, f'{prefix}_photo', photo)
        
        # Display image centered
        x = canvas_width // 2
        y = canvas_height // 2
        canvas.create_image(x, y, image=photo)

    def on_image_click_zoom(self, event, prefix):
        """SIMPLE click to zoom - BACK TO WORKING VERSION!"""
        image_path = getattr(self, f'{prefix}_image_path', None)
        original_image = getattr(self, f'{prefix}_image', None)
        scale = getattr(self, f'{prefix}_scale', 1)
        
        if not image_path or not original_image:
            return
            
        canvas = getattr(self, f'{prefix}_canvas')
        
        # Get canvas dimensions - EXACT SAME as working version!
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        # Get the actual displayed image size
        displayed_width = int(original_image.width * scale)
        displayed_height = int(original_image.height * scale)
        
        # Calculate the image's position on canvas (centered)
        img_left = (canvas_width - displayed_width) // 2
        img_top = (canvas_height - displayed_height) // 2
        
        # Calculate click position relative to the displayed image
        click_on_img_x = event.x - img_left
        click_on_img_y = event.y - img_top
        
        # Check if click is actually on the image
        if (click_on_img_x < 0 or click_on_img_x > displayed_width or 
            click_on_img_y < 0 or click_on_img_y > displayed_height):
            return  # Click was outside the image
        
        # Convert to original image coordinates
        orig_click_x = int(click_on_img_x / scale)
        orig_click_y = int(click_on_img_y / scale)
        
        # Ensure coordinates are within bounds
        orig_click_x = max(0, min(orig_click_x, original_image.width - 1))
        orig_click_y = max(0, min(orig_click_y, original_image.height - 1))
        
        # NOW instead of popup - ZOOM IN-PLACE!
        self.zoom_to_area_in_place(prefix, orig_click_x, orig_click_y)

    def zoom_to_area_in_place(self, prefix, center_x, center_y):
        """Zoom to specific area IN-PLACE - no popup!"""
        canvas = getattr(self, f'{prefix}_canvas')
        original_image = getattr(self, f'{prefix}_image', None)
        
        if not original_image:
            return
            
        canvas.delete("all")
        
        # Get canvas size
        canvas_width = canvas.winfo_width() or 400
        canvas_height = canvas.winfo_height() or 300
        
        # Crop area around click point (300x300 pixels)
        crop_size = 300
        half_crop = crop_size // 2
        
        img_width, img_height = original_image.size
        
        # Calculate crop boundaries
        left = max(0, center_x - half_crop)
        top = max(0, center_y - half_crop) 
        right = min(img_width, center_x + half_crop)
        bottom = min(img_height, center_y + half_crop)
        
        # Crop the area
        cropped_img = original_image.crop((left, top, right, bottom))
        
        # Scale up to fit canvas nicely (2x zoom)
        zoom_factor = 2.0
        new_width = int(cropped_img.width * zoom_factor)
        new_height = int(cropped_img.height * zoom_factor)
        
        # Make sure it fits in canvas
        if new_width > canvas_width - 20:
            zoom_factor = (canvas_width - 20) / cropped_img.width
            new_width = int(cropped_img.width * zoom_factor)
            new_height = int(cropped_img.height * zoom_factor)
            
        if new_height > canvas_height - 20:
            zoom_factor = (canvas_height - 20) / cropped_img.height
            new_width = int(cropped_img.width * zoom_factor)
            new_height = int(cropped_img.height * zoom_factor)
        
        # Resize cropped area
        zoomed_img = cropped_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(zoomed_img)
        
        # Store reference
        setattr(self, f'{prefix}_photo', photo)
        setattr(self, f'{prefix}_zoomed', True)  # Mark as zoomed
        
        # Display zoomed image centered
        x = canvas_width // 2
        y = canvas_height // 2
        canvas.create_image(x, y, image=photo)
        
        # Update zoom info
        setattr(self, f'{prefix}_zoom_level', zoom_factor)
        self.update_zoom_info(prefix)

    def reset_zoom_place(self, prefix):
        """Reset to normal view"""
        setattr(self, f'{prefix}_zoom_level', 1.0)
        setattr(self, f'{prefix}_zoomed', False)
        self.display_image_normal(prefix)
        self.update_zoom_info(prefix)

    def zoom_in_place(self, prefix):
        """Zoom in button - simple"""
        zoomed = getattr(self, f'{prefix}_zoomed', False)
        if not zoomed:
            # If normal view, just zoom center
            original_image = getattr(self, f'{prefix}_image', None)
            if original_image:
                center_x = original_image.width // 2
                center_y = original_image.height // 2
                self.zoom_to_area_in_place(prefix, center_x, center_y)

    def zoom_out_place(self, prefix):
        """Zoom out = reset to normal"""
        self.reset_zoom_place(prefix)

    def on_image_drag(self, event, prefix):
        """Simple drag - not needed for now"""
        pass

    def on_drag_end(self, event, prefix):
        """Simple drag end - not needed for now"""  
        pass

    def on_mouse_wheel(self, event, prefix):
        """Mouse wheel - simple zoom in/out"""
        if event.delta > 0:
            self.zoom_in_place(prefix)
        else:
            self.zoom_out_place(prefix)

    def update_image_display(self, prefix):
        """Not needed - using simpler functions"""
        pass

    def update_zoom_info(self, prefix):
        """Update zoom level display"""
        zoom_info = getattr(self, f'{prefix}_zoom_info', None)
        if zoom_info:
            zoom_level = getattr(self, f'{prefix}_zoom_level', 1.0)
            zoomed = getattr(self, f'{prefix}_zoomed', False)
            if zoomed:
                zoom_info.config(text=f"Zoomed: {zoom_level:.1f}x")
            else:
                zoom_info.config(text="Normal View")

    def show_zoom_popup(self, prefix, image_path, center_x, center_y):
        """Show zoomed area around clicked point with original resolution"""
        if not image_path or not os.path.exists(image_path):
            return
            
        try:
            # Load original image at FULL RESOLUTION
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            # Define crop area - bigger area for better context
            crop_size = 300  # pixels - larger area
            half_crop = crop_size // 2
            
            # Calculate crop boundaries
            left = max(0, center_x - half_crop)
            top = max(0, center_y - half_crop)
            right = min(img_width, center_x + half_crop)
            bottom = min(img_height, center_y + half_crop)
            
            # Crop the area at ORIGINAL RESOLUTION
            cropped_img = img.crop((left, top, right, bottom))
            
            # Create popup window - BIGGER for better viewing
            popup = tk.Toplevel(self.root)
            popup.title(f"🔍 {prefix.title()} Plate - ORIGINAL RESOLUTION")
            popup.geometry("900x700")
            popup.configure(bg='#1a1a1a')
            popup.resizable(True, True)
            
            # Make it always on top for better UX
            popup.transient(self.root)
            popup.grab_set()
            
            # Create main frame
            main_frame = tk.Frame(popup, bg='#1a1a1a')
            main_frame.pack(fill='both', expand=True, padx=5, pady=5)
            
            # START WITH ORIGINAL RESOLUTION - NO SCALING!
            zoom_factor = 1.0  # Keep original resolution
            display_width = int(cropped_img.width * zoom_factor)
            display_height = int(cropped_img.height * zoom_factor)
            
            # Create the initial image at original resolution
            zoomed_img = cropped_img.resize((display_width, display_height), Image.Resampling.LANCZOS)
            photo_popup = ImageTk.PhotoImage(zoomed_img)
            
            # Create scrollable canvas with SMOOTH scrolling
            canvas_frame = tk.Frame(main_frame, bg='#1a1a1a')
            canvas_frame.pack(fill='both', expand=True)
            
            canvas_popup = tk.Canvas(canvas_frame, bg='#1a1a1a', highlightthickness=0, 
                                   cursor='hand2')  # Hand cursor for dragging
            
            # Add SMOOTH scrollbars
            v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas_popup.yview, 
                                     bg='#2c3e50', troughcolor='#1a1a1a')
            h_scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal", command=canvas_popup.xview,
                                     bg='#2c3e50', troughcolor='#1a1a1a')
            canvas_popup.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Pack scrollbars and canvas
            v_scrollbar.pack(side="right", fill="y")
            h_scrollbar.pack(side="bottom", fill="x")
            canvas_popup.pack(side="left", fill="both", expand=True)
            
            # Display image at ORIGINAL RESOLUTION - CENTERED
            image_id = canvas_popup.create_image(0, 0, image=photo_popup, anchor='center')
            
            # Set scroll region and CENTER the image
            canvas_popup.configure(scrollregion=(-display_width//2, -display_height//2, 
                                                display_width//2, display_height//2))
            
            # Keep reference to prevent garbage collection
            canvas_popup.image = photo_popup
            
            # SMOOTH HAND DRAGGING functionality - IMPROVED
            canvas_popup.drag_data = {"x": 0, "y": 0, "dragging": False}
            
            def start_drag(event):
                canvas_popup.drag_data["x"] = canvas_popup.canvasx(event.x)
                canvas_popup.drag_data["y"] = canvas_popup.canvasy(event.y)
                canvas_popup.drag_data["dragging"] = True
                canvas_popup.configure(cursor='hand1')  # Closed hand while dragging
            
            def do_drag(event):
                if canvas_popup.drag_data["dragging"]:
                    # Calculate movement delta
                    new_x = canvas_popup.canvasx(event.x)
                    new_y = canvas_popup.canvasy(event.y)
                    
                    delta_x = new_x - canvas_popup.drag_data["x"]
                    delta_y = new_y - canvas_popup.drag_data["y"]
                    
                    # Move the image smoothly
                    current_x = canvas_popup.coords(image_id)[0]
                    current_y = canvas_popup.coords(image_id)[1]
                    
                    canvas_popup.coords(image_id, current_x + delta_x, current_y + delta_y)
                    
                    # Update drag position
                    canvas_popup.drag_data["x"] = new_x
                    canvas_popup.drag_data["y"] = new_y
            
            def stop_drag(event):
                canvas_popup.drag_data["dragging"] = False
                canvas_popup.configure(cursor='hand2')  # Open hand when not dragging
            
            # Bind smooth dragging events
            canvas_popup.bind("<Button-1>", start_drag)
            canvas_popup.bind("<B1-Motion>", do_drag)
            canvas_popup.bind("<ButtonRelease-1>", stop_drag)
            canvas_popup.bind("<Leave>", stop_drag)  # Stop dragging if mouse leaves
            
            # LIGHTNING FAST mouse wheel zoom
            def fast_mouse_wheel(event):
                # Super responsive zoom
                factor = 1.15 if event.delta > 0 else 0.87  # Faster zoom steps
                self.popup_zoom_fast(popup, canvas_popup, cropped_img, factor, image_id)
            
            canvas_popup.bind("<MouseWheel>", fast_mouse_wheel)
            
            # Add FAST VALIDATION control frame at TOP
            validation_control_frame = tk.Frame(popup, bg='#34495e', height=70)
            validation_control_frame.pack(fill='x', pady=(0, 5))
            validation_control_frame.pack_propagate(False)
            
            # VALIDATION BUTTONS - RIGHT IN THE POPUP!
            validation_frame = tk.Frame(validation_control_frame, bg='#34495e')
            validation_frame.pack(side='left', pady=15, padx=20)
            
            # Current detected value display
            current_detected = self.front_detected_var.get() if prefix == 'front' else self.rear_detected_var.get()
            tk.Label(validation_frame, text=f"🔍 Detected: {current_detected}", 
                    bg='#34495e', fg='#ecf0f1', font=('Arial', 12, 'bold')).pack(side='left', padx=10)
            
            # SUPER FAST VALIDATION BUTTONS
            correct_btn = tk.Button(validation_frame, text="✅ CORRECT", 
                                  font=('Arial', 14, 'bold'), bg='#27ae60', fg='white', 
                                  width=12, height=2, relief='raised', bd=3,
                                  command=lambda: self.popup_validate_correct(popup, prefix))
            correct_btn.pack(side='left', padx=10)
            
            wrong_btn = tk.Button(validation_frame, text="❌ WRONG", 
                                font=('Arial', 14, 'bold'), bg='#e74c3c', fg='white', 
                                width=12, height=2, relief='raised', bd=3,
                                command=lambda: self.popup_validate_wrong(popup, prefix))
            wrong_btn.pack(side='left', padx=5)
            
            # Quick info
            info_frame = tk.Frame(validation_control_frame, bg='#34495e')
            info_frame.pack(side='right', pady=15, padx=20)
            
            tk.Label(info_frame, text=f"⚡ FAST VALIDATE: Click buttons above!", 
                    bg='#34495e', fg='#f39c12', font=('Arial', 10, 'bold')).pack(side='right')
            control_frame.pack(fill='x', pady=(5, 0))
            control_frame.pack_propagate(False)
            
            # Left side - Zoom controls
            zoom_frame = tk.Frame(control_frame, bg='#2c3e50')
            zoom_frame.pack(side='left', pady=15, padx=15)
            
            tk.Button(zoom_frame, text="🔍++ ZOOM IN", 
                     command=lambda: self.popup_zoom_fast(popup, canvas_popup, cropped_img, 1.3, image_id),
                     bg='#27ae60', fg='white', font=('Arial', 11, 'bold'), 
                     relief='flat', padx=15).pack(side='left', padx=3)
            
            tk.Button(zoom_frame, text="🔍-- ZOOM OUT", 
                     command=lambda: self.popup_zoom_fast(popup, canvas_popup, cropped_img, 0.77, image_id),
                     bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'),
                     relief='flat', padx=15).pack(side='left', padx=3)
            
            tk.Button(zoom_frame, text="↺ ORIGINAL SIZE", 
                     command=lambda: self.popup_zoom_fast(popup, canvas_popup, cropped_img, 'reset', image_id),
                     bg='#f39c12', fg='white', font=('Arial', 11, 'bold'),
                     relief='flat', padx=15).pack(side='left', padx=3)
            
            # Center - Resolution info
            info_frame = tk.Frame(control_frame, bg='#2c3e50')
            info_frame.pack(side='right', pady=15, padx=15)
            
            resolution_text = f"📐 Original Resolution: {cropped_img.width}×{cropped_img.height}px"
            tk.Label(info_frame, text=resolution_text, 
                    bg='#2c3e50', fg='#ecf0f1', font=('Arial', 10, 'bold')).pack(side='right')
            
            tk.Label(info_frame, text="🖱️ Drag to move • Wheel to zoom • ESC to close", 
                    bg='#2c3e50', fg='#bdc3c7', font=('Arial', 9)).pack(side='right', padx=(0, 20))
            
            # Store zoom level and original data
            popup.zoom_level = 1.0  # Start at original resolution
            popup.original_crop = cropped_img
            popup.image_id = image_id
            
            # FAST keyboard shortcuts
            def fast_zoom_in(event):
                self.popup_zoom_fast(popup, canvas_popup, cropped_img, 1.2, image_id)
            
            def fast_zoom_out(event):
                self.popup_zoom_fast(popup, canvas_popup, cropped_img, 0.83, image_id)
            
            def reset_zoom(event):
                self.popup_zoom_fast(popup, canvas_popup, cropped_img, 'reset', image_id)
            
            # Bind FAST keyboard shortcuts
            popup.bind("<plus>", fast_zoom_in)
            popup.bind("<equal>", fast_zoom_in)  # = key without shift
            popup.bind("<minus>", fast_zoom_out)
            popup.bind("<r>", reset_zoom)
            popup.bind("<Escape>", lambda e: popup.destroy())
            
            # Focus and center the popup
            popup.focus_set()
            popup.update_idletasks()
            
            # Center the popup on screen
            popup.geometry(f"900x700+{(popup.winfo_screenwidth()//2)-450}+{(popup.winfo_screenheight()//2)-350}")
            
            # CENTER the image in the canvas view
            canvas_popup.update_idletasks()
            canvas_popup.xview_moveto(0.5)
            canvas_popup.yview_moveto(0.5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not create zoom popup: {str(e)}")

    def popup_zoom_fast(self, popup, canvas, original_crop, factor, image_id):
        """LIGHTNING FAST zoom with original resolution preserved"""
        try:
            if factor == 'reset':
                popup.zoom_level = 1.0  # Back to original resolution
            else:
                popup.zoom_level *= factor
                popup.zoom_level = max(0.3, min(8.0, popup.zoom_level))  # Wider zoom range
            
            # Calculate new size - KEEP CRISP RESOLUTION
            new_width = int(original_crop.width * popup.zoom_level)
            new_height = int(original_crop.height * popup.zoom_level)
            
            # Use LANCZOS for crisp scaling
            zoomed_img = original_crop.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(zoomed_img)
            
            # Get current image position
            current_x, current_y = canvas.coords(image_id)
            
            # Update image INSTANTLY with new photo
            canvas.itemconfig(image_id, image=photo)
            canvas.image = photo  # Keep reference
            
            # Update scroll region to accommodate new size
            canvas.configure(scrollregion=(-new_width//2, -new_height//2, 
                                         new_width//2, new_height//2))
            
            # If resetting, center the image
            if factor == 'reset':
                canvas.coords(image_id, 0, 0)  # Center position
                canvas.xview_moveto(0.5)
                canvas.yview_moveto(0.5)
            else:
                # Keep current position during zoom
                canvas.coords(image_id, current_x, current_y)
                
        except Exception as e:
            print(f"Zoom error: {e}")  # Silent error handling for smooth UX
    
    def popup_validate_correct(self, popup, prefix):
        """Handle CORRECT validation from popup window"""
        # Close popup immediately
        popup.destroy()
        
        # Mark as correct (same as clicking correct in main window)
        key = f"{self.current_index}_{prefix}"
        self.validation_results[key] = True
        
        # Add to CSV
        self.add_validated_record(prefix, "correct")
        
        # Visual feedback
        total_validated = len(self.validation_df)
        self.status_var.set(f"✅ {prefix.upper()} CORRECT (from zoom) | Total: {total_validated}")
        self.update_validation_stats()
        
        # Check for auto-advance
        front_key = f"{self.current_index}_front"
        rear_key = f"{self.current_index}_rear"
        
        if front_key in self.validation_results and rear_key in self.validation_results:
            self.root.after(300, self.next_record)
    
    def popup_validate_wrong(self, popup, prefix):
        """Handle WRONG validation from popup window"""
    def show_error_options_in_popup(self, zoom_popup, prefix):
        """Show error options RIGHT IN the zoom popup - no new window!"""
        # Find the validation control frame and hide it temporarily
        for widget in zoom_popup.winfo_children():
            if isinstance(widget, tk.Frame) and widget.cget('bg') == '#34495e':
                widget.pack_forget()
                break
        
        # Create error selection frame
        error_frame = tk.Frame(zoom_popup, bg='#e74c3c', height=120)
        error_frame.pack(fill='x', pady=(0, 5), before=zoom_popup.winfo_children()[0])
        error_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(error_frame, text=f"❌ SELECT ERROR TYPE FOR {prefix.upper()} PLATE", 
                              font=('Arial', 14, 'bold'), bg='#e74c3c', fg='white')
        title_label.pack(pady=(10, 5))
        
        # Error options in 2 rows
        error_options = [
            ("🚫 Hidden/Broken", "hidden_broken"),
            ("❌ Fail", "fail"),
            ("🚗 No License Plate", "no_LP"),
            ("🚙 No Vehicle", "no_vehicle"),
            ("🌫️ Blur", "blur"),
            ("🏍️ Motorcycle", "moto"),
            ("🔄 Wrong Pair", "wrong_pair")
        ]
        
        # First row
        row1_frame = tk.Frame(error_frame, bg='#e74c3c')
        row1_frame.pack(pady=2)
        
        for i, (display_name, error_code) in enumerate(error_options[:4]):
            btn = tk.Button(row1_frame, text=display_name, font=('Arial', 9, 'bold'),
                           bg='#c0392b', fg='white', width=15, height=1,
                           command=lambda code=error_code: self.popup_select_error(zoom_popup, prefix, code))
            btn.pack(side='left', padx=3)
        
        # Second row
        row2_frame = tk.Frame(error_frame, bg='#e74c3c')
        row2_frame.pack(pady=2)
        
        for i, (display_name, error_code) in enumerate(error_options[4:]):
            btn = tk.Button(row2_frame, text=display_name, font=('Arial', 9, 'bold'),
                           bg='#c0392b', fg='white', width=15, height=1,
                           command=lambda code=error_code: self.popup_select_error(zoom_popup, prefix, code))
            btn.pack(side='left', padx=3)
        
        # Cancel button
        cancel_btn = tk.Button(row2_frame, text="↩️ BACK", font=('Arial', 9, 'bold'),
                              bg='#95a5a6', fg='white', width=15, height=1,
                              command=lambda: self.hide_error_options_in_popup(zoom_popup, error_frame))
        cancel_btn.pack(side='left', padx=3)
        
        # Store reference for hiding later
        zoom_popup.error_frame = error_frame
    
    def hide_error_options_in_popup(self, zoom_popup, error_frame):
        """Hide error options and show validation buttons again"""
        error_frame.destroy()
        
        # Show validation frame again
        for widget in zoom_popup.winfo_children():
            if isinstance(widget, tk.Frame) and widget.cget('bg') == '#34495e':
                widget.pack(fill='x', pady=(0, 5), before=zoom_popup.winfo_children()[0])
                break
    
    def popup_select_error(self, zoom_popup, prefix, error_code):
        """Handle error selection from popup"""
        # Close the popup
        zoom_popup.destroy()
        
        # Mark as incorrect
        key = f"{self.current_index}_{prefix}"
        self.validation_results[key] = False
        
        # Add to CSV with error code
        self.add_validated_record(prefix, error_code)
        
        # Visual feedback
        error_display = error_code.replace('_', ' ').title()
        total_validated = len(self.validation_df)
        self.status_var.set(f"❌ {error_display} (from zoom) | Total: {total_validated}")
        self.update_validation_stats()
        
        # Check for auto-advance
        front_key = f"{self.current_index}_front"
        rear_key = f"{self.current_index}_rear"
        
        if front_key in self.validation_results and rear_key in self.validation_results:
            self.root.after(300, self.next_record)
        
    def previous_record(self):
        """Navigate to previous record"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_navigation()
            self.update_display()
            
    def next_record(self):
        """Navigate to next record"""
        if self.df is not None and self.current_index < len(self.df) - 1:
            self.current_index += 1
            self.update_navigation()
            self.update_display()
            
    def mark_validation(self, prefix, is_correct):
        """Mark validation result for current record"""
        key = f"{self.current_index}_{prefix}"
        self.validation_results[key] = is_correct
        
        if is_correct:
            # CORRECT - Add/Update record in CSV with "correct"
            self.add_validated_record(prefix, "correct")
            
            # Visual feedback in status bar - NO POPUP!
            total_validated = len(self.validation_df)
            self.status_var.set(f"✅ {prefix.upper()} CORRECT | Total validated: {total_validated}")
            self.update_validation_stats()
            
        else:
            # WRONG - Show error selection popup
            self.show_error_options(prefix)
            return  # Don't auto-advance yet, wait for error selection
        
        # Check if both plates are validated for auto-advance
        front_key = f"{self.current_index}_front"
        rear_key = f"{self.current_index}_rear"
        
        if front_key in self.validation_results and rear_key in self.validation_results:
            self.root.after(300, self.next_record)  # LIGHTNING FAST auto-advance!
            
    def previous_record(self):
        """Navigate to previous record"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_navigation()
            self.update_display()
            
    def next_record(self):
        """Navigate to next record"""
        if self.df is not None and self.current_index < len(self.df) - 1:
            self.current_index += 1
            self.update_navigation()
            self.update_display()
            
    def mark_validation(self, prefix, is_correct):
        """Mark validation result for current record"""
        key = f"{self.current_index}_{prefix}"
        self.validation_results[key] = is_correct
        
        if is_correct:
            # CORRECT - Add/Update record in CSV with "correct"
            self.add_validated_record(prefix, "correct")
            
            # Visual feedback in status bar - NO POPUP!
            total_validated = len(self.validation_df)
            self.status_var.set(f"✅ {prefix.upper()} CORRECT | Total validated: {total_validated}")
            self.update_validation_stats()
            
        else:
            # WRONG - Show error selection popup
            self.show_error_options(prefix)
            return  # Don't auto-advance yet, wait for error selection
        
        # Check if both plates are validated for auto-advance
        front_key = f"{self.current_index}_front"
        rear_key = f"{self.current_index}_rear"
        
        if front_key in self.validation_results and rear_key in self.validation_results:
            self.root.after(300, self.next_record)  # LIGHTNING FAST auto-advance!
            
    def export_results(self):
        """Export validation results to JSON file (legacy format)"""
        if not self.validation_results:
            messagebox.showwarning("Warning", "No validation results to export")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save validation results (JSON format)",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.validation_results, f, indent=2)
                messagebox.showinfo("Success", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {str(e)}")
    
    def save_current_validation(self):
        """Force save current validation CSV"""
        if self.validation_df is not None:
            try:
                self.validation_df.to_csv(self.csv_output_path, index=False)
                messagebox.showinfo("✅ Saved", f"Validation results saved to:\n{self.csv_output_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save validation CSV: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No validation data to save. Please load a CSV first.")

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = ANPRValidator(root)
    
    # Add menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Load CSV", command=app.load_csv)
    file_menu.add_command(label="Save Validation Results", command=lambda: app.save_current_validation())
    file_menu.add_separator()
    file_menu.add_command(label="Export Old Format", command=app.export_results)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About", 
                         command=lambda: messagebox.showinfo("About", 
                                                            "ANPR Detection Validator Pro\n\n"
                                                            "Professional tool for validating\n"
                                                            "license plate detection results.\n\n"
                                                            "Features:\n"
                                                            "• Load CSV detection results\n"
                                                            "• View front & rear plate images\n"
                                                            "• Click to zoom specific areas\n"
                                                            "• Export validation results\n\n"
                                                            "Built with Python & Tkinter"))
    
    # Keyboard shortcuts
    root.bind('<Left>', lambda e: app.previous_record())
    root.bind('<Right>', lambda e: app.next_record())
    root.bind('<Escape>', lambda e: root.focus_set())  # Clear focus from popups
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
