# =============================================================================
#  ZSCAN - Impedance Measurement Application
#  Version: 1.1.0
#  Developed by: Caju
#  Description: Enhanced GUI application for impedance measurements with LCR meter
#  Requirements: 
#     - Python 3.8+
#     - Tkinter, Matplotlib, Threading
#     - Custom modules: mocklcr.py, lcr.py
#  Last updated: 2024-04-19
# =============================================================================

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import math
import time
import matplotlib.pyplot as plt
from threading import Event, Thread
from datetime import datetime
from typing import List, Tuple
from mocklcr import MockLCRMeter
from lcr import configure_lcr, fetch_measurement


class ImpedanceMeasurementApp:
    """Main application class for impedance measurement."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the application."""
        self.root = root
        self.setup_window()
        self.setup_styles()
        self.setup_widgets()
        
        self.lcr = MockLCRMeter()
        self.measurements: List[Tuple[List[float], List[float], str, str]] = []
        self.stop_event = Event()
        self.measurement_thread = None

    def setup_window(self):
        """Configure the main window properties."""
        self.root.title("ZSCAN - Impedance Measurement App v1.1.0")
        self.root.geometry("600x800")
        self.root.resizable(False, False)
        self.root.option_add("*Font", "Fixedsys 14")
        self.root.configure(bg="#1e1e1e")
        
    def setup_styles(self):
        """Configure custom widget styles."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=6, relief="flat", 
                      font=("Fixedsys", 14), borderwidth=2,
                      foreground="white", background="#333")
        style.map("TButton", 
                background=[('active', '#444'), ('disabled', '#222')],
                foreground=[('active', 'cyan')])
        style.configure("TCombobox", fieldbackground="#333", 
                      background="#333", foreground="white",
                      justify="center")
        style.map("TCombobox", fieldbackground=[('readonly', '#333')])
        style.configure("Horizontal.TProgressbar", thickness=20,
                       troughcolor="#333", background="#4CAF50")
    
    def setup_widgets(self):
        """Create and arrange all GUI widgets."""
        # Header
        self.header_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.header_frame.pack(pady=(10, 5))
        
        self.header_label = tk.Label(
            self.header_frame, 
            text="ZSCAN - v1.1.0",
            font=("Fixedsys", 20, "bold"), 
            fg="cyan", 
            bg="#1e1e1e"
        )
        self.header_label.pack()
        
        # Configuration Frame
        self.config_frame = tk.LabelFrame(
            self.root, 
            text=" Measurement Configuration ", 
            font=("Fixedsys", 12), 
            fg="white", 
            bg="#1e1e1e",
            relief=tk.GROOVE
        )
        self.config_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Measurement Type
        tk.Label(
            self.config_frame, 
            text="Measurement Type:", 
            font=("Fixedsys", 12), 
            fg="white", 
            bg="#1e1e1e"
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.measurement_choice = tk.StringVar(value="PARAMETER")
        self.type_dropdown = ttk.Combobox(
            self.config_frame, 
            textvariable=self.measurement_choice, 
            values=["PARAMETER", "PINS", "HOUSING", "ISLAND", "HOUSING STRIP"],
            state="readonly",
            width=18,
            justify="center"
        )
        self.type_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        # Frequency Configuration
        tk.Label(
            self.config_frame, 
            text="Start Freq (Hz):", 
            font=("Fixedsys", 12), 
            fg="white", 
            bg="#1e1e1e"
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.freq_start = tk.StringVar(value="1000")
        ttk.Entry(
            self.config_frame, 
            textvariable=self.freq_start, 
            width=12,
            justify="center"
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(
            self.config_frame, 
            text="Stop Freq (Hz):", 
            font=("Fixedsys", 12), 
            fg="white", 
            bg="#1e1e1e"
        ).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        self.freq_stop = tk.StringVar(value="1000000")
        ttk.Entry(
            self.config_frame, 
            textvariable=self.freq_stop, 
            width=12,
            justify="center"
        ).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(
            self.config_frame, 
            text="Step Size (Hz):", 
            font=("Fixedsys", 12), 
            fg="white", 
            bg="#1e1e1e"
        ).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        
        self.freq_step = tk.StringVar(value="10000")
        ttk.Entry(
            self.config_frame, 
            textvariable=self.freq_step, 
            width=12,
            justify="center"
        ).grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Control Buttons
        self.button_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.button_frame.pack(pady=15)
        
        button_config = [
            ("Start Measurement", self.start_measurement, "normal"),
            ("Stop Measurement", self.stop_measurement, "disabled"),
            ("End Measurement", self.end_measurement, "normal"),
            ("Generate Graph", self.generate_graph, "normal"),
            ("Save Graph", self.save_graph, "normal"),
            ("Export Data", self.save_txt_data, "normal"),
            ("Exit", self.exit_app, "normal")
        ]
        
        for text, command, state in button_config:
            btn = ttk.Button(
                self.button_frame, 
                text=text, 
                command=command,
                state=state
            )
            btn.pack(pady=8, fill=tk.X, padx=20)
            setattr(self, f"{text.lower().replace(' ', '_')}_button", btn)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.root, 
            orient="horizontal", 
            length=500, 
            mode="determinate",
            style="Horizontal.TProgressbar"
        )
        self.progress.pack(pady=10)
        
        # Status bar
        self.status_frame = tk.Frame(self.root, bg="#1e1e1e", height=30)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar(value="STATUS: IDLE")
        self.status_bar = tk.Label(
            self.status_frame, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor='center', 
            font=("Fixedsys", 12, "bold"), 
            fg="white", 
            bg="#1e1e1e"
        )
        self.status_bar.pack(fill=tk.X)

    def start_measurement(self):
        """Start a new thread for impedance measurement."""
        if len(self.measurements) >= 5:
            messagebox.showinfo("Info", "Maximum of five measurements allowed.")
            return
            
        try:
            self.validate_frequency_inputs()
        except ValueError:
            return
            
        if self.measurement_thread and self.measurement_thread.is_alive():
            messagebox.showwarning("Warning", "Measurement already in progress")
            return
            
        self.measurement_thread = Thread(target=self.measure_impedance, daemon=True)
        self.measurement_thread.start()

    def validate_frequency_inputs(self) -> Tuple[int, int, int]:
        """Validate frequency range inputs."""
        try:
            start = int(self.freq_start.get())
            stop = int(self.freq_stop.get())
            step = int(self.freq_step.get())
            
            if not (0 < start < stop):
                raise ValueError("Start frequency must be less than stop frequency")
            if step <= 0:
                raise ValueError("Step must be positive")
            if step > (stop - start):
                raise ValueError("Step size too large for frequency range")
                
            return start, stop, step
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid frequency parameters: {str(e)}")
            raise

    def measure_impedance(self):
        """Perform impedance measurement sweep."""
        try:
            self.stop_event.clear()
            self.update_ui_for_measurement_start()
            
            mode = "Z"
            start, stop, step = self.validate_frequency_inputs()
            measurement_type = self.measurement_choice.get()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            frequencies = []
            magnitudes = []
            total_steps = (stop - start) // step + 1
            self.progress["maximum"] = total_steps
            
            for i, freq in enumerate(range(start, stop + 1, step)):
                if self.stop_event.is_set():
                    break
                    
                try:
                    configure_lcr(self.lcr, mode, freq)
                    time.sleep(0.5)
                    result = fetch_measurement(self.lcr, mode)
                    real, imag = map(float, result.strip().split(','))
                    magnitude = math.sqrt(real**2 + imag**2)
                    
                    frequencies.append(freq)
                    magnitudes.append(magnitude)
                    
                    self.progress["value"] = i + 1
                    self.status_var.set(f"STATUS: MEASURING {freq/1000:.1f} kHz")
                    self.root.update_idletasks()
                    
                except Exception as e:
                    self.log_error(f"Measurement error at {freq} Hz: {str(e)}")
                    continue
            
            if frequencies:
                self.measurements.append((
                    frequencies, 
                    magnitudes, 
                    measurement_type,
                    timestamp
                ))
                
            self.update_ui_for_measurement_end()
            
        except Exception as e:
            self.log_error(f"Measurement failed: {str(e)}")
            self.update_ui_for_measurement_end()

    def update_ui_for_measurement_start(self):
        """Update UI when measurement starts."""
        self.start_measurement_button.config(state="disabled")
        self.stop_measurement_button.config(state="normal")
        self.end_measurement_button.config(state="disabled")
        self.status_var.set("STATUS: MEASURING...")
        self.status_bar.config(fg="red")
        self.root.update_idletasks()

    def update_ui_for_measurement_end(self):
        """Update UI when measurement ends."""
        self.start_measurement_button.config(state="normal")
        self.stop_measurement_button.config(state="disabled")
        self.end_measurement_button.config(state="normal")
        
        if self.stop_event.is_set():
            self.status_var.set("STATUS: MEASUREMENT STOPPED")
            self.status_bar.config(fg="orange")
        else:
            self.status_var.set("STATUS: MEASUREMENT COMPLETE")
            self.status_bar.config(fg="green")
            
        self.root.update_idletasks()

    def stop_measurement(self):
        """Stop the current measurement."""
        self.stop_event.set()
        self.status_var.set("STATUS: STOPPING...")
        self.status_bar.config(fg="orange")
        self.root.update_idletasks()

    def end_measurement(self):
        """Finalize the measurement session."""
        if not self.measurements:
            messagebox.showwarning("Warning", "No measurements to end")
            return
            
        self.start_measurement_button.config(state="normal")
        self.end_measurement_button.config(state="disabled")
        self.status_var.set("STATUS: READY TO GENERATE GRAPH")
        self.status_bar.config(fg="cyan")
        self.root.update_idletasks()

    def generate_graph(self):
        """Generate impedance vs frequency graph."""
        if not self.measurements:
            messagebox.showerror("Error", "No measurement data available")
            return
            
        plt.figure(figsize=(10, 6), facecolor="#f0f0f0")
        ax = plt.gca()
        ax.set_facecolor("#f8f8f8")
        
        colors = ['b', 'g', 'r', 'c', 'm']
        
        for i, (freqs, mags, label, _) in enumerate(self.measurements):  # Removed timestamp
            color = colors[i % len(colors)]
            plt.semilogx(
                freqs, mags, 
                label=label,  # Simplified label
                color=color,
                linewidth=2
                # Removed markers
            )
        
        # Bold all text elements
        plt.title("Impedance vs Frequency", fontsize=14, pad=20, weight='bold')
        plt.xlabel("Frequency (Hz)", fontsize=12, weight='bold')
        plt.ylabel("|Z| (Ohms)", fontsize=12, weight='bold')
        legend = plt.legend(fontsize=10, framealpha=0.9)
        plt.setp(legend.get_texts(), weight='bold')  # Bold legend text
        
        plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        plt.tight_layout()
        plt.show()

    def save_graph(self):
        """Save the current graph to a file."""
        if not self.measurements:
            messagebox.showwarning("No Data", "No measurements to plot")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPG Image", "*.jpg"),  # Added JPG option
                ("PDF Document", "*.pdf"),
                ("All Files", "*.*")
            ],
            title="Save Graph As"
        )
        
        if not file_path:
            return
            
        try:
            self.generate_graph()
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            messagebox.showinfo("Success", f"Graph saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save graph: {str(e)}")

    def save_txt_data(self):
        """Save measurement data to a text file."""
        if not self.measurements:
            messagebox.showwarning("No Data", "No measurements to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Measurement Data"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, "w") as f:
                f.write("ZSCAN Measurement Data\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for i, (freqs, mags, label, timestamp) in enumerate(self.measurements):
                    f.write(f"=== Measurement {i+1} ===\n")
                    f.write(f"Type: {label}\n")
                    f.write(f"Timestamp: {timestamp}\n")
                    f.write("Frequency (Hz)\tImpedance (Ohms)\n")
                    
                    for freq, mag in zip(freqs, mags):
                        f.write(f"{freq}\t{mag:.4f}\n")
                    f.write("\n")
                    
            messagebox.showinfo("Success", f"Data exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def log_error(self, message: str):
        """Log an error message to status bar and console."""
        print(f"ERROR: {message}")
        self.status_var.set(f"ERROR: {message[:50]}...")
        self.status_bar.config(fg="red")
        self.root.update_idletasks()

    def exit_app(self):
        """Clean up and exit the application."""
        self.stop_event.set()
        if self.measurement_thread and self.measurement_thread.is_alive():
            self.measurement_thread.join(timeout=1)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = ImpedanceMeasurementApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application crashed: {str(e)}")
        raise