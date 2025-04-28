# scanner.py
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal
from filesystem_scanner import find_exe_files, full_scan, quick_scan
import model_runner as lm
import file_handler 

class FullScanWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal()
    choice_needed = pyqtSignal(str, str)
    file_scanning = pyqtSignal(str)

    def __init__(self, window, chosen_model, tærskel, brug_taerskel, parent=None):
        super().__init__(parent)
        self.window = window
        self.chosen_model = chosen_model
        self.tærskel = tærskel
        self.brug_taerskel = brug_taerskel

    def run(self):
        print("Starting fullscan...")
        lm.load_model(self.chosen_model)  # Load the model once at the start
        exe_files = full_scan()  # Call the function from filesystem_scanner
        total_files = len(exe_files)
        processed = 0

        if not os.path.exists(file_handler.LOG_FILE):
            with open(file_handler.LOG_FILE, 'w') as log_file:
                json.dump([], log_file)

        base_dir = Path(__file__).parent
        model_dir = base_dir / "Models" / self.chosen_model

        for filename in exe_files:  # Use exe_files instead of quick_scan
            if filename not in file_handler.processed_files:
                processed += 1
                self.file_scanning.emit(f"File {processed}/{total_files}\n{os.path.basename(filename)}")
                lm.init_model(str(model_dir))
                is_malware, certainty, malware_certainty = lm.run_model(filename)
                
                if self.brug_taerskel:
                    if malware_certainty > self.tærskel:
                        self.choice_needed.emit(filename, os.path.dirname(filename))
                    else:
                        file_handler.log_data(filename, False, verdict="clean")
                else:
                    if is_malware:
                        self.choice_needed.emit(filename, os.path.dirname(filename))
                    else:
                        file_handler.log_data(filename, False, verdict="clean")

        self.finished.emit()
