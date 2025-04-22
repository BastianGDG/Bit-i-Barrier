import os
import json
import time
import tkinter as tk
from tkinter import filedialog

QUARANTINE_PATH = r'C:\Users\theco\OneDrive - NEXT Uddannelse København\Skrivebord\GYM\3.G\Teknikfag\Qurantine\Qurantine_Virus\package\QurantineFolder'
LOG_FILE = 'log.json'
json_data = {}
processed_files = set() 
EXTENTION  = ".exet"


def quarantine(filename,value,PATH):
        print("Quarantining file: ", filename)
        try:
            file_path = os.path.join(PATH, filename)
            print(file_path)
            if os.path.isfile(file_path):
                base_name, _ = os.path.splitext(filename)
            new_file_path = os.path.join(QUARANTINE_PATH, base_name + EXTENTION)
            os.rename(file_path, new_file_path)
            print(f"Renamed: {file_path} -> {new_file_path}")
            log_data(filename,value)
        except Exception as e:
            print(f"An error occurred: {e}")

def log_data(filename,value):
            processed_files.add(filename) 
            i = len(json_data) + 1
            json_data[i] = {
                "filename": filename,
                "timestamp": time.ctime(time.time()),
                "quarantined": value
            }
            print(json_data)
            with open(LOG_FILE, 'r') as log_file:
                logs = json.load(log_file)
                logs.append(json_data[i])
            with open(LOG_FILE, 'w') as log_file:
                json.dump(logs, log_file, indent=4)

def start(value):
    root = tk.Tk()
    root.withdraw()
    PATH = filedialog.askdirectory(title="Select a folder")
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as log_file:
            json.dump([], log_file)
    while True:
        for filename in os.listdir(PATH):
            if filename.endswith(".exe") and filename not in processed_files:
                print("New file detected: ", filename)
                choice = input("Potentially harmful file found, quarantine? (y/n): ")
                if choice == 'y':
                    print("File quarantined: ", filename)
                    value = True
                    quarantine(filename,value,PATH)
                elif choice == 'n':
                    print("File ignored: ", filename)
                    value = False
                    log_data(filename,value)
                else:
                    print("Invalid choice. File ignored.")
        time.sleep(1)
