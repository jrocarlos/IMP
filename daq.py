# daq.py

import nidaqmx
from config import DAQ_DEVICE, NUM_PINS

def setup_daq():
    task = nidaqmx.Task()
    for i in range(NUM_PINS):
        task.do_channels.add_do_chan(f"{DAQ_DEVICE}/port0/line{i}")
    return task

def control_pins(task, active_pins):
    states = [i+1 in active_pins for i in range(NUM_PINS)]
    task.write(states)
