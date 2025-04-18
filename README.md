# ZScan - Impedance Measurement Tool

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.0.0-orange)

A GUI application for automated impedance measurements using LCR meters with frequency sweeping capabilities.

## Features
- **Frequency Sweep Measurements**: Automatically measure impedance across user-defined frequency ranges
- **Vector Analysis**: Calculate and display complex impedance (Z = R + jX)
- **Data Visualization**: Real-time plotting of impedance magnitude/phase vs frequency
- **Multi-Run Support**: Compare multiple measurement runs on the same graph
- **Data Export**: Save measurements as CSV/Excel for further analysis
- **Hardware Integration**: Supports both real LCR meters and simulated devices for testing

## Requirements
| Component       | Version  | Installation Command |
|-----------------|----------|----------------------|
| Python          | 3.8+     | -                    |
| NumPy           | 1.21+    | `pip install numpy`  |
| Matplotlib      | 3.5+     | `pip install matplotlib` |
| PyVISA          | 1.12+    | `pip install pyvisa` |
| pandas          | 1.3+     | `pip install pandas` |
| customtkinter   | 5.2+     | `pip install customtkinter` |

## Hardware Setup
1. Connect your LCR meter via:
   - USB-TMC (for compatible devices)
   - GPIB interface (using NI-VISA)
   - Ethernet (for LAN-enabled instruments)
2. Verify communication using `pyvisa-shell`:
   ```bash
   pyvisa-shell
   > list
   > open "USB0::0x1234::0x5678::MY12345678::INSTR"
   > query("*IDN?")
