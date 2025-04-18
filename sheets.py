# sheets.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SPREADSHEET_NAME

def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client.open(SPREADSHEET_NAME).sheet1

def read_config(sheet):
    trigger = sheet.acell("A1").value.strip().lower()
    dut_label = sheet.acell("B1").value.strip()
    freq_start = int(sheet.acell("B2").value)
    freq_stop = int(sheet.acell("B3").value)
    freq_step = int(sheet.acell("B4").value)
    mode = sheet.acell("B5").value.strip()
    pins = list(map(int, sheet.acell("B7").value.strip().split(',')))
    return trigger, dut_label, freq_start, freq_stop, freq_step, mode, pins

def write_result(sheet, row, timestamp, dut, freq, value, mode, pins):
    sheet.update(f"A{row}", [[timestamp, dut, freq, value, mode, str(pins)]])
