# file_handler.py
import os
import json
import time

QUARANTINE_PATH = r'C:\Users\theco\OneDrive - NEXT Uddannelse København\Skrivebord\GYM\3.G\Teknikfag\Qurantine\Qurantine_Virus\package\QurantineFolder'
LOG_FILE = 'log.json'
json_data = {}
processed_files = set()
EXTENTION = ".exet"

def quarantine(filename, value, PATH):
    print("Quarantining file:", filename)
    try:
        file_path = os.path.join(PATH, filename)
        if os.path.isfile(file_path):
            base_name, _ = os.path.splitext(filename)
            new_file_path = os.path.join(QUARANTINE_PATH, base_name + EXTENTION)
            os.rename(file_path, new_file_path)
            print(f"Renamed: {file_path} -> {new_file_path}")
            log_data(filename, value, verdict="malware")
    except Exception as e:
        print(f"An error occurred: {e}")

def log_data(filename, value, verdict):
    processed_files.add(filename)
    i = len(json_data) + 1
    json_data[i] = {
        "filename": filename,
        "timestamp": time.ctime(time.time()),
        "verdict": verdict,
        "quarantined": value
    }
    print(json_data)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as log_file:
            logs = json.load(log_file)
    else:
        logs = []

    logs.append(json_data[i])

    with open(LOG_FILE, 'w') as log_file:
        json.dump(logs, log_file, indent=4)
