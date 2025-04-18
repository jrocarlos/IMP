# lcr.py

import pyvisa
from config import USE_SIMULATED_LCR, REAL_DEVICE_RESOURCE
from mocklcr import MockLCRMeter

def connect_lcr():
    if USE_SIMULATED_LCR:
        return MockLCRMeter()
    else:
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(REAL_DEVICE_RESOURCE)
        inst.write("*RST")
        return inst

def configure_lcr(inst, mode, freq):
    inst.write(f"FUNC:IMP {mode}")
    inst.write(f"FREQ {freq}")

def fetch_measurement(inst, mode):
    if mode == "Z":
        return inst.query("FETCH:IMPedance?")
    elif mode == "R":
        return inst.query("FETCH:RESistance?")
    elif mode == "C":
        return inst.query("FETCH:CAPacitance?")
    return "0"
