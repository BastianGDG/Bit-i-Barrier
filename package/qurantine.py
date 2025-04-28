# scanner.py
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal

import model_runner as lm
import file_handler 

class ScanWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal()
    choice_needed = pyqtSignal(str, str)  # New signal for handling user choices
    file_scanning = pyqtSignal(str)

    def __init__(self, window, chosen_model, tærskel, brug_taerskel, parent=None):
        super().__init__(parent)
        self.window = window
        self.chosen_model = chosen_model
        self.tærskel = tærskel
        self.brug_taerskel = brug_taerskel
        self.PATH = None

    def set_path(self, path):
        self.PATH = path

    def run(self):  # Changed from start() to run()
        if not self.PATH:
            self.finished.emit()
            return

        print("Starting scan...")
        total_files = len([f for f in os.listdir(self.PATH) if f.endswith(".exe")])
        processed = 0
        if not os.path.exists(file_handler.LOG_FILE):
            with open(file_handler.LOG_FILE, 'w') as log_file:
                json.dump([], log_file)

        base_dir = Path(__file__).parent
        model_dir = base_dir / "Models" / self.chosen_model

        for filename in os.listdir(self.PATH):
            if filename.endswith(".exe") and filename not in file_handler.processed_files:
                processed += 1
                self.progress.emit(f"Progress: {processed}/{total_files}")
                self.file_scanning.emit(filename)  # E
                self.progress.emit(f"Scanning {filename}...")
                lm.init_model(str(model_dir))
                file_path = os.path.join(self.PATH, filename)
                is_malware, certainty, malware_certainty = lm.run_model(file_path)
                
                if self.brug_taerskel:
                    if malware_certainty > self.tærskel:
                        self.choice_needed.emit(filename, self.PATH)
                    else:
                        file_handler.log_data(filename, False, verdict="clean")
                else:
                    if is_malware:
                        self.choice_needed.emit(filename, self.PATH)
                    else:
                        file_handler.log_data(filename, False, verdict="clean")

        self.finished.emit()
