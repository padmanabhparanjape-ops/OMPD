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

from vision.camera import Camera
from vision.yolo_detector import YOLODetector
from vision.face_detector import FaceDetector


class Dashboard(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("OmniGuardian Lite - PrivacyLens")
        self.setGeometry(200, 100, 1000, 700)

        # ---------------- Camera ----------------

        self.camera_device = Camera()
        self.yolo = YOLODetector()
        self.face_detector = FaceDetector()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # ---------------- Title ----------------

        title = QLabel("OmniGuardian Lite")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
        """)

        # ---------------- Camera Preview ----------------

        self.camera = QLabel("Camera Preview")
        self.camera.setMinimumSize(700, 450)
        self.camera.setAlignment(Qt.AlignCenter)
        self.camera.setStyleSheet("""
            border:2px solid black;
            background:#EEEEEE;
        """)

        # ---------------- Buttons ----------------

        self.start_btn = QPushButton("Start Camera")
        self.stop_btn = QPushButton("Stop Camera")
        self.scan_btn = QPushButton("Scan Text")

        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.scan_btn)

        # ---------------- Information ----------------

        self.status = QLabel("Status : Camera Stopped")
        self.privacy = QLabel("Privacy : ACTIVE")
        self.fps = QLabel("FPS : 0")
        self.objects = QLabel("Objects : 0")
        self.face_blur = QLabel("Face Blur : ON")
        self.object_blur = QLabel("Object Blur : ON")
        self.ocr = QLabel("OCR : ON")

        # ---------------- Logs ----------------

        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setPlaceholderText("Detection logs appear here...")

        # ---------------- Layout ----------------

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

    # ---------------- Start Camera ----------------

    def start_camera(self):

        self.camera_device.start()

        self.timer.start(30)

        self.status.setText("Status : Camera Running")

        self.logs.append("Camera Started")

    # ---------------- Stop Camera ----------------

    def stop_camera(self):

        self.timer.stop()

        self.camera_device.stop()

        self.camera.clear()

        self.camera.setText("Camera Preview")

        self.status.setText("Status : Camera Stopped")

        self.logs.append("Camera Stopped")

    # ---------------- Update Camera ----------------

    def update_frame(self):

        frame = self.camera_device.get_frame()

        if frame is None:
            return
        results = self.yolo.detect(frame)
        frame = self.yolo.blur_objects(frame, results)

        faces = self.face_detector.detect(frame)
        frame = self.face_detector.blur_faces(frame, faces)    

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = frame.shape

        bytes_per_line = ch * w

        image = QImage(
            frame.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(image)

        self.camera.setPixmap(
            pixmap.scaled(
                self.camera.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    # ---------------- Close Window ----------------

    def closeEvent(self, event):

        self.stop_camera()

        event.accept()


app = QApplication(sys.argv)

window = Dashboard()

window.show()

sys.exit(app.exec())