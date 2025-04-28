from qurantine import ScanWorker
from quickscan import QuickScanWorker
from file_handler import quarantine, log_data
from fullscan import FullScanWorker
import sys
from pathlib import Path
from functools import partial    
import os
from PyQt6 import QtCore
from PyQt6.QtCore import QSize, Qt, QRect, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QIcon, QCursor
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QPushButton, QLabel, QToolButton, QMessageBox, QFileDialog, QDialog, QFormLayout, QComboBox, QSlider, QDialogButtonBox, QTableWidget, QTableWidgetItem   
)
import json
from filesystem_scanner import find_exe_files, full_scan, quick_scan

base_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = r"Models\[SVM] trained_models(2025-04-24 20-09-03)"  
chosen_model = os.path.abspath(os.path.join(base_dir, relative_path))

class CircularProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._thickness = 15
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._advance)

    def start(self, interval=100):
        """Begin advancing the progress bar."""
        if not self.timer.isActive():
            self.timer.start(interval)

    def reset(self):
        """Reset progress back to 0%."""
        self.timer.stop()
        self._value = 0
        self.update()

    def _advance(self):
        self._value = (self._value + 1) % 101
        self.update()

    def setValue(self, value):
        """Set progress value (0-100)."""
        self._value = min(100, max(0, value))
        self.update()

    def paintEvent(self, event):
        # integer size/margin so we can use QRect
        size   = min(self.width(), self.height())
        margin = self._thickness // 2
        rect   = QRect(margin, margin,
                       size - self._thickness,
                       size - self._thickness)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background circle
        painter.setPen(QPen(QColor("#E0E0E0"), self._thickness))
        painter.drawEllipse(rect)   # QRect works fine here

        # Progress arc
        painter.setPen(QPen(QColor("#2E3A8C"), self._thickness))
        startAngle =  90 * 16
        spanAngle  = -int(self._value * 360 * 16 / 100)
        painter.drawArc(rect, startAngle, spanAngle)
        # Centered text
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Helvetica", int(size/5), QFont.Weight.Light))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{self._value}%")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bit‑i‑Barrier")
        self.resize(1000, 600)
        self.tærskel = 80
        self.brug_taerskel = False  
        
        # === locate your Icons folder ===
        base_dir = Path(__file__).parent
        icons_dir = base_dir / "Icons"                  
        if not icons_dir.exists():  # check if the folder exists
            raise FileNotFoundError(f"Icons folder not found in {base_dir}")    
        base_dir2 = os.path.dirname(os.path.abspath(__file__))
        relative_path = r"Models\[SVM] trained_models(2025-04-24 09-20-49)"  # goes one dir up, then into somefolder
        self.chosen_model = os.path.abspath(os.path.join(base_dir2, relative_path))
        # === root layout ===
        root = QWidget()
        self.setCentralWidget(root)
        main_h = QHBoxLayout(root)
        main_h.setContentsMargins(0,0,0,0)
        main_h.setSpacing(0)

        # --- Sidebar ---
        sidebar = QFrame()
        sidebar.setFixedWidth(100)
        sidebar.setStyleSheet("background-color: #1A1334;")
        sb_v = QVBoxLayout(sidebar)
        sb_v.setAlignment(Qt.AlignmentFlag.AlignTop)
        sb_v.setContentsMargins(10, 20, 10, 20)

        for name in ("radar", "stats"):
            btn = QToolButton()
            path = icons_dir / f"{name}.svg"
            btn.setIcon(QIcon(str(path)))
            btn.setIconSize(QSize(48,48))
            sb_v.addWidget(btn)

        history = QToolButton()
        history.setIcon(QIcon(str(icons_dir / "history.svg")))
        history.setIconSize(QSize(48,48))
        sb_v.addWidget(history)
        sb_v.addStretch()

        # notification bell
        bell = QToolButton()
        bell.setIcon(QIcon(str(icons_dir / "bell.svg")))
        bell.setIconSize(QSize(36,36))
        sb_v.addWidget(bell)
        # little red "1"
        badge = QLabel("1", sidebar)
        badge.setStyleSheet(
            "background:#E63946; color:white;"
            "border-radius:8px; font-size:10px;"
        )
        badge.setFixedSize(16,16)
        # position it over the bell icon
        badge.move(45, 480)

        # settings gear
        gear = QToolButton()
        gear.setIcon(QIcon(str(icons_dir / "gear.svg")))
        gear.setIconSize(QSize(36,36))
        sb_v.addWidget(gear)


        main_h.addWidget(sidebar)
        gear.clicked.connect(self.open_settings)
        history.clicked.connect(self.open_History)
        main_v = QVBoxLayout()
        main_v.setContentsMargins(0,0,0,0)
        fonts_dir = Path(__file__).parent / "Fonts"
        if not fonts_dir.exists():
            raise FileNotFoundError(f"Fonts folder not found in {fonts_dir}")        
        for font_file in fonts_dir.glob("*.ttf"):
            if QFontDatabase.addApplicationFont(str(font_file)) == -1:
                print(f"Failed to load font: {font_file}")
        # header
        header = QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet("background-color: #0E8B3B;")
        hdr_h = QHBoxLayout(header)
        hdr_h.setContentsMargins(20,0,0,0)
        lbl_status = QLabel()
        lbl_status.setStyleSheet("color:white;")
        font_id = QFontDatabase.addApplicationFont("Fonts\Lexend_Exa\LexendExa-VariableFont_wght.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family, 16)
        lbl_status.setFont(font)
        lbl_status.setText(
            "<b>You are safe</b><br>"
            "All shields active<br>"
            "AI is up to date"
        )
        hdr_h.addWidget(lbl_status)
        main_v.addWidget(header)

        # middle split: left buttons / right progress
        split = QHBoxLayout()
        split.setContentsMargins(0,0,0,0)

        # left: scan buttons
        btn_frame = QFrame()
        btn_frame.setStyleSheet("background-color: #3E3F9E;")
        btn_v = QVBoxLayout(btn_frame)
        btn_v.setContentsMargins(50,50,50,50)
        btn_v.setSpacing(30)
        for text, icon in [
            ("Full scan", "drive"),
            ("Custom scan", "file"),
            ("Quick scan", "fast-forward"),
        ]:
            btn = QPushButton(text)
            btn.setIcon(QIcon(str(icons_dir / f"{icon}.svg")))
            btn.setIconSize(QSize(24,24))
            btn.setFont(font)
            btn.setMinimumHeight(60)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0E8B3B;
                    color: white;
                    border-radius: 10px;
                    border: 1px solid #0E8B3B;
                    font-size: 18px;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #28A745;
                }
                QPushButton:pressed {
                    background-color: #1E7E34;
                }
                """
            )
            
            if text == "Custom scan":
                btn.clicked.connect(self.on_custom_scan)  
            elif text == "Quick scan":
                btn.clicked.connect(self.on_quick_scan)
            elif text == "Full scan":
                btn.clicked.connect(self.on_full_scan)
            
            btn_v.addWidget(btn)



        split.addWidget(btn_frame, 1)

        # right: progress
        prog_frame = QFrame()
        prog_frame.setStyleSheet("background-color: #B8C4FF;")
        prog_v = QVBoxLayout(prog_frame)
        prog_v.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress = CircularProgressBar()
        self.progress.setFixedSize(300,300)
        prog_v.addWidget(self.progress)

        # Create label as instance variable directly
        self.lbl_file = QLabel(
            "Ready to scan...\n"
            "No files are processing right now",
        )
        self.lbl_file.setFont(QFont("Roboto", 12))
        self.lbl_file.setStyleSheet("color: #EEE;")
        self.lbl_file.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prog_v.addWidget(self.lbl_file)

        split.addWidget(prog_frame, 2)
        main_v.addLayout(split)

        main_h.addLayout(main_v)

    def update_status(self, message):
        """Update the UI with the current scan progress."""
        print(message)  # Print progress to the console
        # Optionally, update a label or progress bar in the UI
        self.statusBar().showMessage(message)

    def scan_finished(self):
        """Handle the completion of the scan."""
        print("Scan complete!")
        self.statusBar().showMessage("Scan complete!")
        self.lbl_file.setText("Scan complete!\nAll files processed")
        self.progress.setValue(100)  # Set to 100% when done
    
    def open_settings(self):
        print("Settings button clicked")
        dlg = SettingsDialog(self, self.tærskel)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.chosen_model = dlg.model_combo.currentText()
            self.tærskel = dlg.slider1.value()
            param_b = dlg.slider2.value()
            self.brug_taerskel = dlg.brug_taerskel
            print("New settings:", self.chosen_model, self.tærskel, param_b, self.brug_taerskel)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            relative_path = rf"Models\{self.chosen_model}"
            self.chosen_model = os.path.abspath(os.path.join(base_dir, relative_path))
            print("Chosen model path:", self.chosen_model)
        else:
            print("Settings cancelled")

    def on_custom_scan(self):
        print("Custom scan button clicked")
        print(f"Using model: {self.chosen_model}")
        
        # Create the scan worker
        self.scan_worker = ScanWorker(self, self.chosen_model, self.tærskel, self.brug_taerskel)
        
        # Get the path first
        PATH = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Scan",
            ""
        )
        if not PATH:
            return
            
        # Calculate total files before starting
        total_files = len([f for f in os.listdir(PATH) if f.endswith(".exe")])
        self.total_files = total_files
        
        # Set up connections
        self.scan_worker.progress.connect(self.update_status)
        self.scan_worker.finished.connect(self.scan_finished)
        self.scan_worker.choice_needed.connect(self.choice)
        self.scan_worker.file_scanning.connect(self.update_current_file)
        
        # Reset progress bar at start
        self.progress.setValue(0)
        
        # Set the path and start the thread
        self.scan_worker.set_path(PATH)
        self.scan_worker.start()

    def on_quick_scan(self):
        print("Quick scan button clicked")
        print(f"Quick model: {self.chosen_model}")
        
        # Create the scan worker
        self.scan_worker = QuickScanWorker(self, self.chosen_model, self.tærskel, self.brug_taerskel)
        
            
        # Calculate total files before starting
        total_files = len(quick_scan())
        self.total_files = total_files
        
        # Set up connections
        self.scan_worker.progress.connect(self.update_status)
        self.scan_worker.finished.connect(self.scan_finished)
        self.scan_worker.choice_needed.connect(self.choice)
        self.scan_worker.file_scanning.connect(self.update_current_file)
        
        # Reset progress bar at start
        self.progress.setValue(0)
        
        self.scan_worker.start()

    def on_full_scan(self):
        print("Full scan button clicked")
        print(f"Full model: {self.chosen_model}")
        
        # Create the scan worker
        self.scan_worker = FullScanWorker(self, self.chosen_model, self.tærskel, self.brug_taerskel)
        
            
        # Calculate total files before starting
        total_files = len(full_scan())
        self.total_files = total_files
        
        # Set up connections
        self.scan_worker.progress.connect(self.update_status)
        self.scan_worker.finished.connect(self.scan_finished)
        self.scan_worker.choice_needed.connect(self.choice)
        self.scan_worker.file_scanning.connect(self.update_current_file)
        
        # Reset progress bar at start
        self.progress.setValue(0)
        
        self.scan_worker.start()


    def update_current_file(self, filename):
        """Update the label showing current file being scanned"""
        current_file = int(filename.split('/')[0].split()[1])
        progress = int((current_file / self.total_files) * 100)
        self.progress.setValue(progress)
        self.lbl_file.setText(f"Now scanning {filename}...")

    def open_History(self):
        dlg = HistoryDialog(self)
        dlg.exec()

    def choice(self, filename,PATH):
        """Handle the user's choice."""
        choice = QMessageBox.question(
            self,
            "Potentially harmful file found",
            f"File {filename} detected. Quarantine?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        print(PATH, "PATH")
        if choice == QMessageBox.StandardButton.Yes:
            print("File quarantined: ", filename)
            value = True
            quarantine(filename,value,PATH)
        else:
            print("File ignored: ", filename)
            value = False
            log_data(filename,value,verdict="malware")    

class SettingsDialog(QDialog):
    def __init__(self, parent=None, tærskel=50):  # Default value for tærskel
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(300, 200)

        self.tærskel = tærskel  # Store tærskel as an instance attribute

        form = QFormLayout()
        # Model Dropdown menu
        self.model_combo = QComboBox()
        specific_path = Path(__file__).parent / "Models"

        # Add folder names to the combo box
        if specific_path.exists() and specific_path.is_dir():
            folder_names = [folder.name for folder in specific_path.iterdir() if folder.is_dir()]
            self.model_combo.addItems(folder_names)
        else:
            self.model_combo.addItems(["Fast", "Thorough"])

        # Set the current model as the default selection
        if parent and hasattr(parent, "chosen_model"):
            current_model = Path(parent.chosen_model).name
            index = self.model_combo.findText(current_model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)

        form.addRow("AI model:", self.model_combo)
        # Slider 1
        self.slider1 = QSlider(Qt.Orientation.Horizontal)
        self.slider1.setRange(0, 100)
        self.slider1.setValue(self.tærskel)  # Use the passed tærskel value
        # Indsæt efter self.slider1 definitionen
        self.slider1_label = QLabel(f"Tærskel: {self.tærskel}")
        self.slider1.valueChanged.connect(self.update_slider1_label)
        form.addRow(self.slider1_label, self.slider1)

        # Slider 2
        self.slider2 = QSlider(Qt.Orientation.Horizontal)
        self.slider2.setRange(0, 10)
        self.slider2.setValue(5)
        form.addRow("Parameter 2:", self.slider2)

        # BrugTærskel toggle
        self.brug_taerskel = False  # Default value
        self.toggle_button = QPushButton("Brug Tærskel: OFF")
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_brug_taerskel)
        form.addRow("Brug Tærskel:", self.toggle_button)
 
        # --- OK / Cancel ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # Layout
        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(buttons)

    def update_slider1_label(self, value):
        self.slider1_label.setText(f"Tærskel: {value}")
        
    def toggle_brug_taerskel(self):
        self.brug_taerskel = self.toggle_button.isChecked()
        if self.brug_taerskel:
            self.toggle_button.setText("Brug Tærskel: ON")
        else:
            self.toggle_button.setText("Brug Tærskel: OFF")
            self.slider1.setValue(0) # Reset slider to 0 when toggled
class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("History")
        self.setModal(True)
        self.resize(490, 160)

        # Load json file
        with open("log.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print(data)

        # Create table with 3 columns
        table = QTableWidget(len(data), 4, self)
        table.setHorizontalHeaderLabels(["Filename", "Timestamp", "Verdict","Quarantined"])
        table.setColumnWidth(0,150)
        table.setColumnWidth(1,150)
        table.setColumnWidth(2,70)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Fill table
        for row, entry in enumerate(data):
            table.setItem(row, 0, QTableWidgetItem(entry["filename"]))
            table.setItem(row, 1, QTableWidgetItem(entry["timestamp"]))
            table.setItem(row, 2, QTableWidgetItem(entry["verdict"]))
            yesno = "Yes" if entry["quarantined"] else "No"
            table.setItem(row, 3, QTableWidgetItem(yesno))

        # Layout
        lay = QVBoxLayout(self)
        lay.addWidget(table)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    base_dir = Path(__file__).parent
    icon_path = base_dir / "Icons" / "app_icon.ico"
    app.setWindowIcon(QIcon(str(icon_path)))
    w = MainWindow()   
    w.show()
    sys.exit(app.exec())