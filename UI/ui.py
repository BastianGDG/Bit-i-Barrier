import sys
from pathlib import Path
from functools import partial    

from PyQt6 import QtCore
from PyQt6.QtCore import QSize, Qt, QRect, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QIcon, QCursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QPushButton, QLabel, QToolButton, QMessageBox, QFileDialog    
)

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

        # === locate your Icons folder ===
        base_dir = Path(__file__).parent
        icons_dir = base_dir / "Icons"

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

        for name in ("radar", "stats", "history"):
            btn = QToolButton()
            path = icons_dir / f"{name}.svg"
            btn.setIcon(QIcon(str(path)))
            btn.setIconSize(QSize(48,48))
            sb_v.addWidget(btn)

        sb_v.addStretch()

        # notification bell
        bell = QToolButton()
        bell.setIcon(QIcon(str(icons_dir / "bell.svg")))
        bell.setIconSize(QSize(36,36))
        sb_v.addWidget(bell)
        # little red “1”
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

        main_v = QVBoxLayout()
        main_v.setContentsMargins(0,0,0,0)

        # header
        header = QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet("background-color: #0E8B3B;")
        hdr_h = QHBoxLayout(header)
        hdr_h.setContentsMargins(20,0,0,0)
        lbl_status = QLabel(
            "You are safe\n"
            "All shields active\n"
            "AI is up to date"
        )
        lbl_status.setStyleSheet("color:white;")
        lbl_status.setFont(QFont("Arial", 16, QFont.Weight.DemiBold))
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
            else:
                btn.clicked.connect(partial(self.scan, mode=text))
            
            btn_v.addWidget(btn)



        split.addWidget(btn_frame, 1)

        # right: progress
        prog_frame = QFrame()
        prog_frame.setStyleSheet("background-color: #B8C4FF;")
        prog_v = QVBoxLayout(prog_frame)
        prog_v.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # store it as an instance attribute so on_custom_scan can see it:
        self.progress = CircularProgressBar()
        self.progress.setFixedSize(300,300)
        prog_v.addWidget(self.progress)
        lbl_file = QLabel(
            "Now scanning GrænseværdiLog_kontinuitet.pdf…\n"
            "File 32403/56705"
        )
        lbl_file.setFont(QFont("Arial", 12))
        lbl_file.setStyleSheet("color: #EEE;")
        lbl_file.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prog_v.addWidget(lbl_file)

        split.addWidget(prog_frame, 2)
        main_v.addLayout(split)

        main_h.addLayout(main_v)


    def scan(self, mode):
        """Stub handler for Full / Quick scan."""
        QMessageBox.information(
            self,
            f"{mode} Scan",
            f"{mode} scan started!"
        )

    def on_custom_scan(self):
        # reset & kickoff the progress animation
        self.progress.reset()
        self.progress.start(interval=100)   # 100 ms steps
 
        # you can still do your file‑dialog or other logic:
        path, _ = QFileDialog.getOpenFileName(self,
            "Select folder or file to scan")
        if path:
            QMessageBox.information(self, "Custom Scan",
                                    f"Scanning: {path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    base_dir = Path(__file__).parent
    icon_path = base_dir / "Icons" / "app_icon.ico"
    app.setWindowIcon(QIcon(str(icon_path)))
    w = MainWindow()   
    w.show()
    sys.exit(app.exec())
