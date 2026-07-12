import sys
import cv2

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
)

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap

from vision.text_detector import TextDetector
from database.database import Database
from vision.camera import Camera
from vision.yolo_detector import YOLODetector
from vision.face_detector import FaceDetector


class Dashboard(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("OmniGuardian Lite - PrivacyLens")
        self.setGeometry(200, 100, 1000, 700)

        # ---------------- Backend ----------------
        self.camera_device = Camera()
        self.db = Database()
        self.yolo = YOLODetector(db=self.db)
        self.text_detector = TextDetector()
        self.current_frame = None

        # Face detector safe loading
        try:
            self.face_detector = FaceDetector()
            self.face_enabled = True
        except Exception as e:
            print("Face detector disabled:", e)
            self.face_detector = None
            self.face_enabled = False

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # ---------------- UI ----------------
        title = QLabel("OmniGuardian Lite")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:24px; font-weight:bold;")

        # Camera display
        self.camera = QLabel("Camera Preview")
        self.camera.setMinimumSize(700, 450)
        self.camera.setAlignment(Qt.AlignCenter)
        self.camera.setStyleSheet("border:2px solid black; background:#EEEEEE;")

        # Buttons
        self.start_btn = QPushButton("Start Camera")
        self.stop_btn = QPushButton("Stop Camera")
        self.scan_btn = QPushButton("Scan Text")

        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)
        self.scan_btn.clicked.connect(self.scan_text)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.scan_btn)

        # Status
        self.status = QLabel("Status : Camera Stopped")
        self.privacy = QLabel("Privacy : ACTIVE")
        self.fps = QLabel("FPS : 0")
        self.objects = QLabel("Objects : 0")
        self.face_blur = QLabel("Face Blur : ON")
        self.object_blur = QLabel("Object Blur : ON")
        self.ocr = QLabel("OCR : ON")

        # Logs
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setPlaceholderText("Detection logs appear here...")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.camera)
        layout.addLayout(button_layout)
        layout.addWidget(self.status)
        layout.addWidget(self.privacy)
        layout.addWidget(self.fps)
        layout.addWidget(self.objects)
        layout.addWidget(self.face_blur)
        layout.addWidget(self.object_blur)
        layout.addWidget(self.ocr)
        layout.addWidget(self.logs)

        self.setLayout(layout)

    # ---------------- Camera Start ----------------
    def start_camera(self):
        self.camera_device.start()
        self.timer.start(30)
        self.status.setText("Status : Camera Running")
        self.logs.append("Camera Started")

    # ---------------- Camera Stop ----------------
    def stop_camera(self):
        self.timer.stop()
        self.camera_device.stop()
        self.camera.clear()
        self.camera.setText("Camera Preview")
        self.status.setText("Status : Camera Stopped")
        self.logs.append("Camera Stopped")

    # ---------------- Logs ----------------
    def update_logs(self):
        logs = self.db.get_recent_logs()
        self.logs.clear()
        for log in reversed(logs):
            timestamp, event_type, label, confidence = log
            self.logs.append(f"{timestamp} | {event_type} | {label} | {confidence:.2f}")

    # ---------------- Frame Update ----------------
    def update_frame(self):
        frame = self.camera_device.get_frame()
        if frame is None:
            return

        # Object Detection
        results = self.yolo.detect(frame)
        # Uncomment when object blur is needed
        # frame = self.yolo.blur_objects(frame, results)

        # Face Detection
        if self.face_enabled:
            faces = self.face_detector.detect(frame)
            frame = self.face_detector.blur_faces(frame, faces)

        # Text Detection
        text_results = self.text_detector.detect(frame)
        frame = self.text_detector.blur_text(frame, text_results)

        self.current_frame = frame.copy()
        self.update_logs()

        # Display
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)

        self.camera.setPixmap(
            pixmap.scaled(
                self.camera.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # ---------------- OCR Scan ----------------
    def scan_text(self):
        if self.current_frame is None:
            self.logs.append("No frame available.")
            return

        frame = self.current_frame.copy()
        results = self.text_detector.detect(frame)
        frame = self.text_detector.blur_text(frame, results)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        image = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)

        self.camera.setPixmap(
            pixmap.scaled(
                self.camera.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        self.logs.append("OCR Scan Completed")

    # ---------------- Close ----------------
    def closeEvent(self, event):
        self.stop_camera()
        self.db.close()
        event.accept()


# ---------------- Main ----------------
app = QApplication(sys.argv)
window = Dashboard()
window.show()
sys.exit(app.exec())
