import os
import json
import time
from PyQt6.QtWidgets import ( QFileDialog    
)
import model_runner as lm


QUARANTINE_PATH = r'C:\Users\theco\OneDrive - NEXT Uddannelse København\Skrivebord\GYM\3.G\Teknikfag\Qurantine\Qurantine_Virus\package\QurantineFolder'
LOG_FILE = 'log.json'
json_data = {}
processed_files = set() 
EXTENTION  = ".exet"
verdict = "clean"

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
            log_data(filename,value,verdict="malware")
        except Exception as e:
            print(f"An error occurred: {e}")

def log_data(filename,value,verdict):
            processed_files.add(filename) 
            i = len(json_data) + 1
            json_data[i] = {
                "filename": filename,
                "timestamp": time.ctime(time.time()),
                "verdict": verdict,
                "quarantined": value
            }
            print(json_data)
            with open(LOG_FILE, 'r') as log_file:
                logs = json.load(log_file)
                logs.append(json_data[i])
            with open(LOG_FILE, 'w') as log_file:
                json.dump(logs, log_file, indent=4)

def start(window):
    PATH = QFileDialog.getExistingDirectory(
        window,
        "Select Folder to Scan",
        ""
    )
    print("Starting scan...")
    print(PATH)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as log_file:
            json.dump([], log_file)

    for filename in os.listdir(PATH):
        if filename.endswith(".exe") and filename not in processed_files:
            print("New file detected: ", filename)
            model_dir = r'C:\Users\theco\Downloads\[SVM] trained_models(2025-04-24 09-20-49)'
            lm.init_model(model_dir)
            file = os.path.join(PATH, filename)
            is_malware, certainty, malware_certainty = lm.run_model(file)
            print(f"Is malware: {is_malware}, Certainty: {certainty}, Malware Certainty: {malware_certainty}")  
            if is_malware:
                print("-\t File Evaluation: Malware")
                from ui import MainWindow
                MainWindow().choice(filename, PATH)
            else:
                print("-\t File Evaluation: Clean")
                log_data(filename, False,verdict="clean")