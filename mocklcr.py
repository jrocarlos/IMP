# mocklcr.py

import random

class MockLCRMeter:
    def __init__(self):
        self.freq = 1000
        self.mode = "Z"

    def write(self, command):
        if command.startswith("FREQ"):
            self.freq = float(command.split()[1])
        elif command.startswith("FUNC"):
            self.mode = command.split()[1]

    def query(self, command):
        if command.startswith("FETCH"):
            if self.mode == "Z":
                Z_real = round(random.uniform(10, 100), 2)
                Z_imag = round(random.uniform(-50, 50), 2)
                return f"{Z_real},{Z_imag}"
            elif self.mode == "R":
                return str(round(random.uniform(5, 100), 2))
            elif self.mode == "C":
                return str(round(random.uniform(1e-9, 1e-6), 12))
        return "0"
