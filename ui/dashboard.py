import sys
import time
import cv2
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QWidget
)

from vision.camera import Camera
from vision.yolo_detector import YOLODetector
from vision.face_detector import FaceDetector
from vision.text_detector import TextDetector
from database.database import Database
from ui.ui_builder import build_ui


class Dashboard(QWidget):

    def __init__(self):
        super().__init__()

        # ===============================
        # Window
        # ===============================
        self.setWindowTitle("OMPD - PrivacyLens")
        self.resize(1700, 950)
        self.setMinimumSize(1500, 850)

        # ===============================
        # Backend
        # ===============================
        self.camera_device = Camera()
        self.db = Database()
        self.yolo = YOLODetector(db=self.db)
        self.text_detector = TextDetector()

        try:
            self.face_detector = FaceDetector()
            self.face_enabled = True
        except Exception:
            self.face_detector = None
            self.face_enabled = False

        # ===============================
        # Runtime State
        # ===============================
        self.current_frame = None
        self.object_blur_enabled = True
        self.ocr_enabled = True

        self.blur_strength = 15
        self.yolo_conf = 0.50

        self.session_start = None
        self.session_frames = 0

        self._last_frame_time = None
        self._fps_smoothed = 0

        self._cached_faces = []
        self._cached_yolo = []
        self._cached_text = []

        self.yolo_every_n = 3
        self.face_every_n = 2
        self.ocr_every_n = 15

        self.frame_counter = 0

        # ===============================
        # Timer
        # ===============================
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        # ===============================
        # Build Interface
        # ===============================
        build_ui(self)
    
    # ======================================================
    # CAMERA START
    # ======================================================

    def start_camera(self):

        try:

            self.camera_device.start()

            self.session_start = time.time()
            self.session_frames = 0

            self.frame_counter = 0

            self.camera_status.setText("● Live")
            self.status.setText("Camera Started")
            self.session_info.setText("Session Running")

            self.logs.append("Camera Started")

            self.timer.start(30)

        except Exception as e:

            self.logs.append(f"Failed to start camera : {e}")
            self.status.setText("Camera Error")

    # ======================================================
    # CAMERA STOP
    # ======================================================

    def stop_camera(self):

        self.timer.stop()

        try:
            self.camera_device.stop()
        except:
            pass

        self.camera.clear()
        self.camera.setText("Camera Preview")

        self.camera_status.setText("● Offline")
        self.status.setText("Camera Stopped")
        self.session_info.setText("Session Finished")

        self.logs.append("Camera Stopped")

        if self.session_start is not None:

            duration = int(time.time() - self.session_start)

            self.logs.append(
                f"Session Duration : {duration}s"
            )

    # ======================================================
    # UPDATE FPS
    # ======================================================

    def update_fps(self):

        now = time.time()

        if self._last_frame_time is not None:

            delta = now - self._last_frame_time

            if delta > 0:

                fps = 1.0 / delta

                if self._fps_smoothed == 0:

                    self._fps_smoothed = fps

                else:

                    self._fps_smoothed = (
                        self._fps_smoothed * 0.9
                        + fps * 0.1
                    )

                self.fps.setText(
                    f"FPS : {self._fps_smoothed:.1f}"
                )

                self.fps_value.setText(
                    f"{self._fps_smoothed:.1f}"
                )

        self._last_frame_time = now

    # ======================================================
    # UPDATE FRAME
    # ======================================================

    def update_frame(self):

        frame = self.camera_device.get_frame()

        if frame is None:
            return

        self.session_frames += 1
        self.frame_counter += 1

        self.update_fps()

        # -----------------------------------------
        # YOLO
        # -----------------------------------------

        if self.frame_counter % self.yolo_every_n == 0:

            self._cached_yolo = self.yolo.detect(frame)

        detections = self._cached_yolo

        self.objects_value.setText(
            str(len(detections))
        )

        # -----------------------------------------
        # FACE DETECTION
        # -----------------------------------------

        if self.face_enabled:

            if self.frame_counter % self.face_every_n == 0:

                self._cached_faces = (
                    self.face_detector.detect(frame)
                )

            frame = self.face_detector.blur_faces(
                frame,
                self._cached_faces,
                self.blur_strength
            )

        self.faces_value.setText(
            str(len(self._cached_faces))
        )

        # -----------------------------------------
        # OCR
        # -----------------------------------------

        if self.ocr_enabled:

            if self.frame_counter % self.ocr_every_n == 0:

                self._cached_text = (
                    self.text_detector.detect(frame)
                )

            frame = self.text_detector.blur_text(
                frame,
                self._cached_text,
                self.blur_strength
            )

        self.text_value.setText(
            str(len(self._cached_text))
        )

        # -----------------------------------------
        # OBJECT BLUR
        # -----------------------------------------

        if self.object_blur_enabled:

            try:

                frame = self.yolo.blur_objects(
    frame,
    detections,
    self.blur_strength
)

            except TypeError:

                frame = self.yolo.blur_objects(
                    frame,
                    self._cached_yolo
                )

        self.current_frame = frame.copy()
                # -----------------------------------------
        # PRIVACY SCORE
        # -----------------------------------------

        privacy_score = 100

        privacy_score -= len(self._cached_faces) * 2
        privacy_score -= len(detections) * 3
        privacy_score -= len(self._cached_text) * 5

        privacy_score = max(0, privacy_score)

        self.privacy_value.setText(
            str(privacy_score)
        )

        self.privacy_score.setText(
            f"Privacy : {privacy_score}"
        )

        # -----------------------------------------
        # THREAT LEVEL
        # -----------------------------------------

        if privacy_score >= 85:

            threat = "LOW"

        elif privacy_score >= 60:

            threat = "MEDIUM"

        else:

            threat = "HIGH"

        self.threat_value.setText(threat)

        # -----------------------------------------
        # UPDATE SESSION TIMER
        # -----------------------------------------

        if self.session_start is not None:

            elapsed = int(
                time.time() - self.session_start
            )

            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60

            self.session_label.setText(
                f"Session {hours:02}:{minutes:02}:{seconds:02}"
            )

        # -----------------------------------------
        # REFRESH DATABASE LOGS
        # -----------------------------------------

        if self.frame_counter % 15 == 0:

            self.refresh_activity()

        # -----------------------------------------
        # DISPLAY IMAGE
        # -----------------------------------------

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        h, w, ch = rgb.shape

        image = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(image)

        self.camera.setPixmap(
            pixmap.scaled(
                self.camera.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # ======================================================
    # ACTIVITY CENTER
    # ======================================================

    def refresh_activity(self):

        try:

            logs = self.db.get_recent_logs()

        except Exception:

            return

        self.logs.clear()

        for log in reversed(logs):

            timestamp, event, label, confidence = log

            if confidence >= 0.90:

                icon = "🟥"

            elif confidence >= 0.70:

                icon = "🟨"

            else:

                icon = "🟩"

            self.logs.append(

                f"""
{icon} {event}

Object : {label}

Confidence : {confidence:.2f}

Time : {timestamp}

──────────────────────────────
"""
            )

    # ======================================================
    # BLUR SLIDER
    # ======================================================

    def on_blur_slider_changed(self, value):

        self.blur_strength = value

        self.blur_slider_label.setText(
            f"Blur Strength : {value}"
        )

    # ======================================================
    # CONFIDENCE SLIDER
    # ======================================================

    def on_conf_slider_changed(self, value):

        self.yolo_conf = value / 100

        self.conf_slider_label.setText(
            f"Confidence : {self.yolo_conf:.2f}"
        )

        if hasattr(self.yolo, "conf"):

            self.yolo.conf = self.yolo_conf

    # ======================================================
    # SENSITIVE OBJECTS
    # ======================================================

    def on_sensitive_class_toggled(
    self,
    class_name,
    state
    ):

        enabled = bool(state)

        self.yolo.sensitive_objects[class_name] = enabled

        self.logs.append(
            f"{class_name}: {'Enabled' if enabled else 'Disabled'}"
        )
    # ======================================================
    # PRIVACY SCAN
    # ======================================================

    def scan_text(self):

        if self.current_frame is None:

            self.logs.append(
                "No frame available for Privacy Scan."
            )
            return

        frame = self.current_frame.copy()

        try:

            results = self.text_detector.detect(frame)

        except Exception as e:

            self.logs.append(
                f"OCR Error : {e}"
            )
            return

        try:

            frame = self.text_detector.blur_text(
                frame,
                results,
                self.blur_strength
            )

        except TypeError:

            frame = self.text_detector.blur_text(
                frame,
                results
            )

        self.text_value.setText(str(len(results)))

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        h, w, ch = rgb.shape

        image = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(image)

        self.camera.setPixmap(

            pixmap.scaled(

                self.camera.size(),

                Qt.KeepAspectRatio,

                Qt.SmoothTransformation

            )
        )

        self.logs.append(
            "Privacy Scan Completed"
        )

        self.status.setText(
            "Privacy Scan Complete"
        )

    # ======================================================
    # FACE BLUR
    # ======================================================

    def toggle_face_blur(self):

        self.face_enabled = not self.face_enabled

        state = "ON" if self.face_enabled else "OFF"

        self.face_blur.setText(
            f"Face Blur : {state}"
        )

        self.logs.append(
            f"Face Blur {state}"
        )

    # ======================================================
    # OBJECT BLUR
    # ======================================================

    def toggle_object_blur(self):

        self.object_blur_enabled = (
            not self.object_blur_enabled
        )

        state = (
            "ON"
            if self.object_blur_enabled
            else "OFF"
        )

        self.object_blur.setText(
            f"Object Blur : {state}"
        )

        self.logs.append(
            f"Object Blur {state}"
        )

    # ======================================================
    # OCR
    # ======================================================

    def toggle_ocr(self):

        self.ocr_enabled = (
            not self.ocr_enabled
        )

        state = (
            "ON"
            if self.ocr_enabled
            else "OFF"
        )

        self.ocr.setText(
            f"OCR : {state}"
        )

        self.logs.append(
            f"OCR {state}"
        )

    # ======================================================
    # CLOSE EVENT
    # ======================================================

    def closeEvent(self, event):

        self.stop_camera()

        try:

            self.db.close()

        except Exception:

            pass

        event.accept()


# ==========================================================
# APPLICATION
# ==========================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    style = (
        Path(__file__).parent.parent
        / "assets"
        / "style.qss"
    )

    if style.exists():

        with open(
            style,
            "r",
            encoding="utf-8"
        ) as f:

            app.setStyleSheet(
                f.read()
            )

    window = Dashboard()

    window.show()

    sys.exit(
        app.exec()
    )
