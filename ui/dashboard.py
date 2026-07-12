import sys
import time
import cv2

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QSlider,
    QScrollArea,
    QCheckBox,
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
        self.setGeometry(200, 100, 1000, 850)

        # ---------------- Backend ----------------
        self.camera_device = Camera()
        self.db = Database()
        self.yolo = YOLODetector(db=self.db)
        self.text_detector = TextDetector()
        self.current_frame = None

        # ---------------- New state (toggles / sliders / fps) ----------------
        self.object_blur_enabled = True
        self.ocr_enabled = True
        self.blur_strength = 15          # Gaussian blur kernel-ish strength, 1-100
        self.yolo_conf = 0.50            # mirrors self.yolo.conf
        self._last_frame_time = None
        self._fps_smoothed = 0.0

        # Which object classes are eligible for blurring. Keys must match
        # whatever label string your YOLODetector returns per-detection
        # (COCO class names shown here - adjust if yolo_detector.py uses
        # different strings, e.g. "cellphone" instead of "cell phone").
        self.sensitive_classes = {
            "cell phone": True,
            "book": True,
        }

        # Frame-throttling: run expensive detectors every N frames instead of
        # every frame, and reuse cached results in between. This is the main
        # lever for FPS - OCR in particular is expensive to run every frame.
        self._frame_counter = 0
        self.yolo_every_n = 3     # run object detection every 3rd frame
        self.face_every_n = 2     # run face detection every 2nd frame
        self.ocr_every_n = 15     # run OCR every 15th frame (heaviest step)
        self.logs_every_n = 10    # refresh the log/db view every 10th frame
        self._cached_yolo_results = []
        self._cached_faces = []
        self._cached_text_results = []

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
        self.toggle_face_btn = QPushButton("Toggle Face Blur")
        self.toggle_object_btn = QPushButton("Toggle Object Blur")
        self.toggle_ocr_btn = QPushButton("Toggle OCR/Text Blur")

        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)
        self.scan_btn.clicked.connect(self.scan_text)
        self.toggle_face_btn.clicked.connect(self.toggle_face_blur)
        self.toggle_object_btn.clicked.connect(self.toggle_object_blur)
        self.toggle_ocr_btn.clicked.connect(self.toggle_ocr)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.scan_btn)
        button_layout.addWidget(self.toggle_face_btn)
        button_layout.addWidget(self.toggle_object_btn)
        button_layout.addWidget(self.toggle_ocr_btn)

        # Status
        self.status = QLabel("Status : Camera Stopped")
        self.privacy = QLabel("Privacy : ACTIVE")
        self.fps = QLabel("FPS : 0")
        self.objects = QLabel("Objects : 0")
        self.face_blur = QLabel("Face Blur : ON")
        self.object_blur = QLabel("Object Blur : ON")
        self.ocr = QLabel("OCR : ON")

        # New detection counter labels
        self.faces_count_label = QLabel("Faces : 0")
        self.sensitive_text_label = QLabel("Sensitive Text : 0")

        # ---------------- Sensitive object checkboxes ----------------
        self.sensitive_objects_label = QLabel("Blur only these objects:")
        self.checkbox_phone = QCheckBox("Phone")
        self.checkbox_phone.setChecked(self.sensitive_classes["cell phone"])
        self.checkbox_phone.stateChanged.connect(
            lambda state: self.on_sensitive_class_toggled("cell phone", state)
        )

        self.checkbox_book = QCheckBox("Book")
        self.checkbox_book.setChecked(self.sensitive_classes["book"])
        self.checkbox_book.stateChanged.connect(
            lambda state: self.on_sensitive_class_toggled("book", state)
        )

        sensitive_checkbox_layout = QHBoxLayout()
        sensitive_checkbox_layout.addWidget(self.sensitive_objects_label)
        sensitive_checkbox_layout.addWidget(self.checkbox_phone)
        sensitive_checkbox_layout.addWidget(self.checkbox_book)

        # Blur strength slider
        self.blur_slider_label = QLabel(f"Blur Strength : {self.blur_strength}")
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(1, 100)
        self.blur_slider.setValue(self.blur_strength)
        self.blur_slider.valueChanged.connect(self.on_blur_slider_changed)

        # Confidence slider (0.10 - 1.00, stored as int 10-100)
        self.conf_slider_label = QLabel(f"Confidence : {self.yolo_conf:.2f}")
        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setRange(10, 100)
        self.conf_slider.setValue(int(self.yolo_conf * 100))
        self.conf_slider.valueChanged.connect(self.on_conf_slider_changed)

        # Apply initial confidence to the detector if it exposes .conf
        if hasattr(self.yolo, "conf"):
            self.yolo.conf = self.yolo_conf

        slider_layout = QVBoxLayout()
        slider_layout.addLayout(sensitive_checkbox_layout)
        slider_layout.addWidget(self.blur_slider_label)
        slider_layout.addWidget(self.blur_slider)
        slider_layout.addWidget(self.conf_slider_label)
        slider_layout.addWidget(self.conf_slider)

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
        layout.addWidget(self.faces_count_label)
        layout.addWidget(self.sensitive_text_label)
        layout.addWidget(self.face_blur)
        layout.addWidget(self.object_blur)
        layout.addWidget(self.ocr)
        layout.addLayout(slider_layout)
        layout.addWidget(self.logs)

        # Put all content in a scrollable container so nothing (like the
        # sliders) ever gets hidden below the visible window area.
        content_widget = QWidget()
        content_widget.setLayout(layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll_area)

        self.setLayout(outer_layout)

    # ---------------- Camera Start ----------------
    def start_camera(self):
        self.camera_device.start()
        self.timer.start(30)
        self.status.setText("Status : Camera Running")
        self.logs.append("Camera Started")
        self._last_frame_time = None
        print("Camera started")

    # ---------------- Camera Stop ----------------
    def stop_camera(self):
        self.timer.stop()
        self.camera_device.stop()
        self.camera.clear()
        self.camera.setText("Camera Preview")
        self.status.setText("Status : Camera Stopped")
        self.logs.append("Camera Stopped")
        print("Camera stopped")

    # ---------------- Logs ----------------
    def update_logs(self):
        logs = self.db.get_recent_logs()
        self.logs.clear()
        for log in reversed(logs):
            timestamp, event_type, label, confidence = log
            self.logs.append(f"{timestamp} | {event_type} | {label} | {confidence:.2f}")

    # ---------------- FPS ----------------
    def _update_fps(self):
        now = time.time()
        if self._last_frame_time is not None:
            delta = now - self._last_frame_time
            if delta > 0:
                instant_fps = 1.0 / delta
                # simple smoothing so the number doesn't jitter wildly
                if self._fps_smoothed == 0.0:
                    self._fps_smoothed = instant_fps
                else:
                    self._fps_smoothed = (0.9 * self._fps_smoothed) + (0.1 * instant_fps)
                self.fps.setText(f"FPS : {self._fps_smoothed:.1f}")
        self._last_frame_time = now

    # ---------------- Slider callbacks ----------------
    def on_blur_slider_changed(self, value):
        self.blur_strength = value
        self.blur_slider_label.setText(f"Blur Strength : {self.blur_strength}")

    def on_conf_slider_changed(self, value):
        self.yolo_conf = value / 100.0
        self.conf_slider_label.setText(f"Confidence : {self.yolo_conf:.2f}")
        if hasattr(self.yolo, "conf"):
            self.yolo.conf = self.yolo_conf

    # ---------------- Sensitive-object checkbox callback ----------------
    def on_sensitive_class_toggled(self, class_name, state):
        self.sensitive_classes[class_name] = bool(state)
        enabled = [name for name, on in self.sensitive_classes.items() if on]
        msg = f"Blur classes updated: {', '.join(enabled) if enabled else 'none'}"
        print(msg)
        self.logs.append(msg)

    # ---------------- Object label extraction / filtering ----------------
    def _extract_label(self, detection):
        """
        Best-effort extraction of a class label string from a single
        detection entry, since detector output format can vary.
        Adjust this if you know the exact structure returned by
        YOLODetector.detect().
        """
        if isinstance(detection, dict):
            for key in ("label", "class_name", "name", "class"):
                if key in detection:
                    return str(detection[key]).lower()
            return None

        if isinstance(detection, (list, tuple)):
            for item in detection:
                if isinstance(item, str):
                    return item.lower()
            return None

        for attr in ("label", "class_name", "name", "cls_name"):
            if hasattr(detection, attr):
                val = getattr(detection, attr)
                if isinstance(val, str):
                    return val.lower()

        return None

    def _filter_results_by_enabled_classes(self, results):
        """
        Returns only the detections whose label matches a currently
        checked sensitive class. If a detection's label can't be
        determined (unrecognized detector output format), it is kept
        so blurring doesn't silently stop working - narrow
        _extract_label() above once you confirm the real format.
        """
        enabled = {name.lower() for name, on in self.sensitive_classes.items() if on}
        if not enabled:
            return []

        filtered = []
        for detection in results:
            label = self._extract_label(detection)
            if label is None or label in enabled:
                filtered.append(detection)
        return filtered

    # ---------------- Frame Update ----------------
    def update_frame(self):
        frame = self.camera_device.get_frame()
        if frame is None:
            return

        self._update_fps()
        self._frame_counter += 1

        # Object Detection (throttled - only re-run every yolo_every_n frames)
        if self._frame_counter % self.yolo_every_n == 0:
            self._cached_yolo_results = self.yolo.detect(frame)
        results = self._cached_yolo_results
        print(f"Detected {len(results)} objects")
        self.objects.setText(f"Objects : {len(results)}")

        # Object Blur (only if toggle enabled and detector supports it) -
        # restricted to the classes checked in the sensitive-objects UI
        if self.object_blur_enabled:
            blur_targets = self._filter_results_by_enabled_classes(results)
            if hasattr(self.yolo, "blur_objects"):
                try:
                    frame = self.yolo.blur_objects(frame, blur_targets, self.blur_strength)
                except TypeError:
                    # detector's blur_objects may not accept blur_strength
                    frame = self.yolo.blur_objects(frame, blur_targets)

        # Face Detection (throttled - only re-run every face_every_n frames)
        faces = []
        if self.face_enabled:
            if self._frame_counter % self.face_every_n == 0:
                self._cached_faces = self.face_detector.detect(frame)
            faces = self._cached_faces
            print(f"Detected {len(faces)} faces")
            try:
                frame = self.face_detector.blur_faces(frame, faces, self.blur_strength)
            except TypeError:
                frame = self.face_detector.blur_faces(frame, faces)
            print("Blurring faces...")
        self.faces_count_label.setText(f"Faces : {len(faces)}")

        # Text Detection (throttled - OCR is the heaviest step by far,
        # so it runs on a much longer interval than the other detectors)
        text_results = []
        if self.ocr_enabled:
            if self._frame_counter % self.ocr_every_n == 0:
                self._cached_text_results = self.text_detector.detect(frame)
            text_results = self._cached_text_results
            print(f"Detected {len(text_results)} text regions")
            try:
                frame = self.text_detector.blur_text(frame, text_results, self.blur_strength)
            except TypeError:
                frame = self.text_detector.blur_text(frame, text_results)
            print("Blurring text...")
        self.sensitive_text_label.setText(f"Sensitive Text : {len(text_results)}")

        self.current_frame = frame.copy()

        # DB log refresh is also throttled - no need to hit the database
        # on every single frame
        if self._frame_counter % self.logs_every_n == 0:
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
            print("No frame available for OCR scan")
            return

        frame = self.current_frame.copy()
        results = self.text_detector.detect(frame)
        print(f"OCR scan detected {len(results)} text regions")
        try:
            frame = self.text_detector.blur_text(frame, results, self.blur_strength)
        except TypeError:
            frame = self.text_detector.blur_text(frame, results)
        print("Blurring text during OCR scan...")
        self.sensitive_text_label.setText(f"Sensitive Text : {len(results)}")

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
        print("OCR scan completed")

    # ---------------- Toggle Face Blur ----------------
    def toggle_face_blur(self):
        self.face_enabled = not self.face_enabled
        self.face_blur.setText(f"Face Blur : {'ON' if self.face_enabled else 'OFF'}")
        if self.face_enabled:
            print("Face blur enabled")
            self.logs.append("Face blur enabled")
        else:
            print("Face blur disabled")
            self.logs.append("Face blur disabled")

    # ---------------- Toggle Object Blur ----------------
    def toggle_object_blur(self):
        self.object_blur_enabled = not self.object_blur_enabled
        self.object_blur.setText(f"Object Blur : {'ON' if self.object_blur_enabled else 'OFF'}")
        if self.object_blur_enabled:
            print("Object blur enabled")
            self.logs.append("Object blur enabled")
        else:
            print("Object blur disabled")
            self.logs.append("Object blur disabled")

    # ---------------- Toggle OCR / Text Blur ----------------
    def toggle_ocr(self):
        self.ocr_enabled = not self.ocr_enabled
        self.ocr.setText(f"OCR : {'ON' if self.ocr_enabled else 'OFF'}")
        if self.ocr_enabled:
            print("OCR/text blur enabled")
            self.logs.append("OCR/text blur enabled")
        else:
            print("OCR/text blur disabled")
            self.logs.append("OCR/text blur disabled")

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