# main.py

import time
from datetime import datetime
from sheets import connect_sheet, read_config, write_result
from daq import setup_daq, control_pins
from lcr import connect_lcr, configure_lcr, fetch_measurement

def main():
    print("Starting measurement system...")
    sheet = connect_sheet()
    lcr = connect_lcr()
    daq_task = setup_daq()

    row = 10  # Start writing results here

    while True:
        trigger, dut, f_start, f_stop, f_step, mode, pins = read_config(sheet)

        if trigger == "run":
            print("Running measurement...")
            control_pins(daq_task, pins)

            for freq in range(f_start, f_stop + 1, f_step):
                configure_lcr(lcr, mode, freq)
                time.sleep(0.1)
                value = fetch_measurement(lcr, mode)
                timestamp = datetime.now().isoformat()
                write_result(sheet, row, timestamp, dut, freq, value, mode, pins)
                print(f"{freq} Hz: {value}")
                row += 1

            sheet.update("A1", "done")
            print("Measurement complete.")
        time.sleep(1)

if __name__ == "__main__":
    main()
