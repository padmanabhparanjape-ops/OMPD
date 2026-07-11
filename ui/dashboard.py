from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit
)

import sys


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OmniGuardian Lite - PrivacyLens")
        self.setGeometry(200, 100, 900, 600)

        # Title
        title = QLabel("OmniGuardian Lite")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        # Camera placeholder
        self.camera = QLabel("Camera Preview")
        self.camera.setMinimumHeight(300)
        self.camera.setStyleSheet(
            "border: 2px solid black;"
            "font-size: 20px;"
            "qproperty-alignment: AlignCenter;"
        )

        # Buttons
        start_btn = QPushButton("Start Camera")
        stop_btn = QPushButton("Stop Camera")

        # Status
        self.status = QLabel("Status: System Ready")

        # Logs
        self.logs = QTextEdit()
        self.logs.setPlaceholderText("Detection logs appear here...")
        self.logs.setReadOnly(True)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(start_btn)
        button_layout.addWidget(stop_btn)

        # Main layout
        layout = QVBoxLayout()

        layout.addWidget(title)
        layout.addWidget(self.camera)
        layout.addLayout(button_layout)
        layout.addWidget(self.status)
        layout.addWidget(self.logs)

        self.setLayout(layout)


app = QApplication(sys.argv)

window = Dashboard()
window.show()

sys.exit(app.exec())