# =============================================================================
#  ZScan - Impedance Measurement Application
#  Version: 1.0.0
#  Developed by: Caju
#  Description: A GUI-based Python application to perform impedance measurements
#               using an LCR meter. Measurements can be swept across frequencies
#               and visualized in a graph. Allows multiple measurement runs.
#  Requirements: 
#     - Python 3.x
#     - Tkinter for GUI
#     - Matplotlib for plotting
#     - Custom modules: mocklcr.py, lcr.py
#  Last updated: 2025-04-17
# =============================================================================

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import math
import time
import matplotlib.pyplot as plt
from threading import Event, Thread
from mocklcr import MockLCRMeter
from lcr import configure_lcr, fetch_measurement

class ImpedanceMeasurementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZScan - Impedance Measurement App v1.0.0")
        self.root.geometry("500x650")
        self.root.resizable(False, False)
        self.root.option_add("*Font", "Fixedsys 14")
        self.root.configure(bg="#1e1e1e")

        self.lcr = MockLCRMeter()
        self.measurements = []
        self.stop_event = Event()

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=6, relief="flat", font=("Fixedsys", 14), borderwidth=2,
                        foreground="white", background="#333", focuscolor="#555")
        style.map("TButton", background=[('active', '#444')], foreground=[('active', 'red')])
        style.configure("TCombobox", fieldbackground="#333", background="#333", foreground="white")
        style.map("TCombobox", fieldbackground=[('readonly', '#333')])

        # Header frame
        self.header_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.header_frame.pack(pady=(10, 10))
        self.header_label = tk.Label(self.header_frame, text="ZScan - v1.0.0", font=("Fixedsys", 20, "bold"), fg="cyan", bg="#1e1e1e")
        self.header_label.pack()

        # Controls frame
        self.controls_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.controls_frame.pack(pady=10)

        self.dropdown_label = tk.Label(self.controls_frame, text="Select Measurement:", font=("Fixedsys", 14), fg="white", bg="#1e1e1e")
        self.dropdown_label.pack(pady=(10, 0))

        self.measurement_choice = tk.StringVar()
        self.measurement_dropdown = ttk.Combobox(self.controls_frame, textvariable=self.measurement_choice, state="readonly",
                                                  values=["PARAMETER","PINS", "HOUSING", "ISLAND", "HOUSING STRIP"], justify="center")
        self.measurement_dropdown.pack(pady=5)
        self.measurement_dropdown.current(0)

        # Button frame
        self.button_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.button_frame.pack(pady=20)

        self.measure_button = ttk.Button(self.button_frame, text="Measure", command=self.start_measurement_thread)
        self.measure_button.pack(pady=5)

        self.stop_button = ttk.Button(self.button_frame, text="Stop Measurement", command=self.stop_measurement)
        self.stop_button.pack(pady=5)
        self.stop_button.config(state="disabled")

        self.end_button = ttk.Button(self.button_frame, text="End Measurement", command=self.end_measurement)
        self.end_button.pack(pady=5)

        self.generate_button = ttk.Button(self.button_frame, text="Generate Graph", command=self.generate_graph)
        self.generate_button.pack(pady=5)

        self.save_button = ttk.Button(self.button_frame, text="Save Graph", command=self.save_graph)
        self.save_button.pack(pady=5)

        self.save_txt_button = ttk.Button(self.button_frame, text="Save Data as TXT", command=self.save_txt_data)
        self.save_txt_button.pack(pady=5)

        self.exit_button = ttk.Button(self.button_frame, text="Exit", command=self.exit_app)
        self.exit_button.pack(pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Status frame
        self.status_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_var = tk.StringVar()
        self.status_var.set("STATUS: IDLE")
        self.status_bar = tk.Label(self.status_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor='center', 
                                   font=("Fixedsys", 14, "bold"), fg="white", bg="#1e1e1e")
        self.status_bar.pack(fill=tk.X)

    def start_measurement_thread(self):
        thread = Thread(target=self.measure_impedance)
        thread.start()

    def measure_impedance(self):
        if len(self.measurements) >= 5:
            messagebox.showinfo("Info", "Maximum of five measurements allowed.")
            return

        self.stop_event.clear()
        self.measure_button.config(state="disabled")
        self.end_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_var.set("STATUS: MEASURING...")
        self.status_bar.config(fg="red")
        self.root.update_idletasks()

        mode = "Z"
        freq_start = 1_000
        freq_stop = 1_000_000
        freq_step = 10_000

        total_steps = (freq_stop - freq_start) // freq_step + 1
        self.progress["maximum"] = total_steps
        self.progress["value"] = 0

        frequencies = []
        magnitudes = []

        for i, freq in enumerate(range(freq_start, freq_stop + 1, freq_step)):
            if self.stop_event.is_set():
                break
            configure_lcr(self.lcr, mode, freq)
            time.sleep(1)  # Simulate measurement delay
            result = fetch_measurement(self.lcr, mode)
            try:
                real, imag = map(float, result.strip().split(','))
                magnitude = math.sqrt(real**2 + imag**2)
                frequencies.append(freq)
                magnitudes.append(magnitude)
            except ValueError:
                continue

            self.progress["value"] = i + 1
            self.root.update_idletasks()

        self.measurements.append((frequencies, magnitudes, self.measurement_choice.get()))

        self.status_var.set("STATUS: MEASUREMENT COMPLETE")
        self.status_bar.config(fg="green")
        self.measure_button.config(state="normal")
        self.end_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def stop_measurement(self):
        self.stop_event.set()
        self.status_var.set("STATUS: MEASUREMENT STOPPED")
        self.status_bar.config(fg="orange")

    def end_measurement(self):
        if not self.measurements:
            messagebox.showwarning("Warning", "No measurement to end.")
            return
        self.measure_button.config(state="disabled")
        self.end_button.config(state="disabled")
        self.status_var.set("STATUS: MEASUREMENT ENDED. READY TO GENERATE GRAPH")
        self.status_bar.config(fg="green")

    def generate_graph(self):
        if not self.measurements:
            messagebox.showerror("Error", "No data to graph. Please measure first.")
            return

        plt.figure(figsize=(10, 6))

        for freqs, mags, label in self.measurements:
            plt.semilogx(freqs, mags, label=f"Measurement {label}")

        plt.title("Impedance vs Frequency")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("|Z| (Ohms)")
        plt.legend()
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.tight_layout()
        plt.show()

    def save_graph(self):
        if not self.measurements:
            messagebox.showwarning("No Data", "Measure first before saving graph.")
            return

        plt.figure(figsize=(10, 6))
        for f, m, label in self.measurements:
            plt.semilogx(f, m, label=f"Measurement {label}")

        plt.title("Impedance vs Frequency")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("|Z| (Ohms)")
        plt.legend()
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.tight_layout()
        plt.savefig("impedance_graph.png")
        messagebox.showinfo("Saved", "Graph saved as impedance_graph.png")

    def save_txt_data(self):
        if not self.measurements:
            messagebox.showwarning("No Data", "Measure first before saving data.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        with open(file_path, "w") as f:
            for freqs, mags, label in self.measurements:
                f.write(f"Measurement {label}\n")
                for freq, mag in zip(freqs, mags):
                    f.write(f"{freq}\t{mag:.4f}\n")
                f.write("\n")

        messagebox.showinfo("Saved", f"Data saved as {file_path}")

    def exit_app(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImpedanceMeasurementApp(root)
    root.mainloop()
