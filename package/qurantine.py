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

    def __init__(self, window, chosen_model, tærskel, brug_taerskel, parent=None):
        super().__init__(parent)
        self.window = window
        self.chosen_model = chosen_model
        self.tærskel = tærskel
        self.brug_taerskel = brug_taerskel

    def start(self):
        PATH = QFileDialog.getExistingDirectory(
            self.window,
            "Select Folder to Scan",
            ""
        )
        if not PATH:
            self.finished.emit()
            return

        print("Starting scan...")

        if not os.path.exists(file_handler.LOG_FILE):
            with open(file_handler.LOG_FILE, 'w') as log_file:
                json.dump([], log_file)

        base_dir = Path(__file__).parent
        model_dir = base_dir / "Models" / self.chosen_model

        for filename in os.listdir(PATH):
            if filename.endswith(".exe") and filename not in file_handler.processed_files:
                self.progress.emit(f"Scanning {filename}...")
                print(f"Chosen model: {model_dir}")
                lm.init_model(str(model_dir))
                file_path = os.path.join(PATH, filename)
                print("Using file:", file_path)
                is_malware, certainty, malware_certainty = lm.run_model(file_path)
                if self.brug_taerskel == True:
                    if malware_certainty > self.tærskel:
                        print("-\t File Evaluation: Malware (med tærskel)")
                        print(f"-\t Certainty: {certainty} (med tærskel)")
                        from ui import MainWindow
                        MainWindow().choice(filename, PATH)
                    else:
                        print("-\t File Evaluation: Clean (med tærskel)")
                        print(f"-\t Certainty: {certainty} (med tærskel)") 
                        from file_handler import log_data
                        log_data(filename, False,verdict="clean")
                else:
                    if is_malware:
                        print("-\t File Evaluation: Malware")
                        from ui import MainWindow
                        MainWindow().choice(filename, PATH)
                    else:
                        print("-\t File Evaluation: Clean")
                        from file_handler import log_data
                        log_data(filename, False,verdict="clean")

        self.finished.emit()
