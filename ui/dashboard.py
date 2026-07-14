import sys
import time
import cv2
import csv
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QTableWidgetItem,
    QFileDialog
)

 
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from vision.barcode_detector import QRBarcodeDetector
from vision.text_detector import TextDetector
from database.database import Database

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
        self.barcode_detector = QRBarcodeDetector()

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
        self.last_scan = None
        self.current_scan_image = None
        self.protected_scan_image = None
        self.object_blur_enabled = True
        self.ocr_enabled = True
        self.barcode_enabled = True

        self.blur_strength = 15
        self.yolo_conf = 0.50

        self.session_start = None
        self.session_frames = 0

        self._last_frame_time = None
        self._fps_smoothed = 0

        self._cached_faces = []
        self._cached_yolo = []
        self._cached_text = []
        self._cached_barcodes = []

        # ---------------------------------
        # Prevent duplicate history entries
        # ---------------------------------
        self.logged_faces = set()
        self.logged_objects = set()
        self.logged_text = set()

        self.yolo_every_n = 3
        self.face_every_n = 2
        self.ocr_every_n = 15
        self.barcode_every_n = 5

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

        current_objects = set()

        for obj in detections:
            
            label = obj["label"]
            confidence = obj["confidence"]

            if not self.yolo.sensitive_objects.get(label, False):
                continue

            current_objects.add(label)

            if label not in self.logged_objects:

                self.db.log_detection(
                    "Sensitive Object",
                    label,
                    confidence
                )

                self.logged_objects.add(label)

        # Remove objects that disappeared
        self.logged_objects.intersection_update(current_objects)

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
        # Log face only once while visible
        if self.face_enabled and len(self._cached_faces) > 0:

            if "Human Face" not in self.logged_faces:

                self.db.log_detection(
                    "Face",
                    "Human Face",
                    1.0
                )

                self.logged_faces.add("Human Face")

        else:

            self.logged_faces.clear()

        # -----------------------------------------
        # OCR
        # -----------------------------------------

        if self.ocr_enabled:

            if self.frame_counter % self.ocr_every_n == 0:

                self._cached_text = (
                    self.text_detector.detect(frame)
                )

                current_text = set()

                for bbox, text, confidence in self._cached_text:

                    if not self.text_detector.is_sensitive(text):
                        continue

                    current_text.add(text)

                    if text not in self.logged_text:

                        self.db.log_detection(
                            "Sensitive Text",
                            text,
                            confidence
                        )

                        self.logged_text.add(text)

                # Remove text that disappeared
                self.logged_text.intersection_update(current_text)

                for bbox, text, confidence in self._cached_text:
                    if self.text_detector.is_sensitive(text):
                        self.db.log_detection(
                            "Sensitive Text",
                            text,
                            confidence
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
        # QR / BARCODE DETECTION
        # -----------------------------------------

        if self.barcode_enabled:

            if self.frame_counter % self.barcode_every_n == 0:

                self._cached_barcodes = (
                    self.barcode_detector.detect(frame)
                )

            frame = self.barcode_detector.blur_codes(
                frame,
                self._cached_barcodes,
                self.blur_strength
            )

        self.barcode_value.setText(
            str(len(self._cached_barcodes))
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
        privacy_score -= len(self._cached_barcodes) * 4

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

    def show_scan_preview(self, frame):

        self.last_scan = frame.copy()

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

        self.scan_preview.setPixmap(
            pixmap.scaled(
                self.scan_preview.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    def scan_text(self):

        self.scan_text_button.setEnabled(False)

        try:

            camera_started_here = False

            # --------------------------------------------------
            # Get image for scanning
            # --------------------------------------------------

            if self.current_scan_image is not None:

                # Use uploaded image
                frame = self.current_scan_image.copy()

            else:

                # Use live camera
                if self.camera_device.cap is None:

                    self.camera_device.start()
                    camera_started_here = True

                frame = self.camera_device.get_frame()

                if frame is None:

                    self.logs.append(
                        "Unable to capture image."
                    )
                    return

                frame = frame.copy()

            # --------------------------------------------------
            # OCR Detection
            # --------------------------------------------------

            try:

                results = self.text_detector.detect(frame)

                self.scan_results.setRowCount(0)

                for bbox, text, confidence in results:

                    row = self.scan_results.rowCount()

                    self.scan_results.insertRow(row)

                    self.scan_results.setItem(
                        row,
                        0,
                        QTableWidgetItem("Sensitive Text")
                    )

                    self.scan_results.setItem(
                        row,
                        1,
                        QTableWidgetItem(text)
                    )

                    self.scan_results.setItem(
                        row,
                        2,
                        QTableWidgetItem("HIGH")
                    )

                    self.scan_results.setItem(
                        row,
                        3,
                        QTableWidgetItem(
                            f"{confidence*100:.1f}%"
                        )
                    )

                    if self.text_detector.is_sensitive(text):

                        self.db.log_detection(
                            "Sensitive Text",
                            text,
                            confidence
                        )

            except Exception as e:

                self.logs.append(
                    f"OCR Error : {e}"
                )
                return

            # --------------------------------------------------
            # Blur Sensitive Text
            # --------------------------------------------------

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

            # --------------------------------------------------
            # Update Counter
            # --------------------------------------------------

            self.text_value.setText(
                str(len(results))
            )
            score = max(0, 100 - len(results) * 10)

            self.scan_score.setText(
                f"Privacy Score : {score}"
            )

            if score >= 85:

                threat = "LOW"

            elif score >= 60:

                threat = "MEDIUM"

            else:

                threat = "HIGH"

            self.scan_threat.setText(
                f"Threat : {threat}"
            )

            self.scan_sensitive.setText(
                f"Sensitive Text : {len(results)}"
            )

            self.scan_time.setText(
                time.strftime(
                    "Last Scan : %H:%M:%S"
                )
            )
            
            self.protected_scan_image = frame.copy()

            self.preview_title.setText("🛡 Protected Image")

            self.show_scan_preview(frame)

            if len(results) == 0:

                recommendation = (
                    "No sensitive text detected.\n\n"
                    "This image appears safe."
                )

            elif len(results) <= 2:

                recommendation = (
                    "Small amount of sensitive text detected.\n\n"
                    "Review before sharing."
                )

            else:

                recommendation = (
                    "Multiple sensitive texts detected.\n\n"
                    "Blur before sharing."
                )

            self.scan_recommendation.setText(
                recommendation
            )

            # --------------------------------------------------
            # Logs
            # --------------------------------------------------

            self.logs.append(
                f"📸 Privacy Scan Completed ({len(results)} sensitive text found)"
            )

            self.refresh_history()

            self.status.setText(
                "Privacy Scan Complete"
            )

            # --------------------------------------------------
            # If we opened the camera, close it again
            # --------------------------------------------------

            if camera_started_here:

                self.camera_device.stop()

        except Exception as e:

            self.logs.append(
                f"Privacy Scan Error : {e}"
            )

        finally:

            self.scan_text_button.setEnabled(True)

    def upload_image(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_name:
            return

        image = cv2.imread(file_name)

        if image is None:
            self.status.setText("Failed to load image.")
            return

        self.current_scan_image = image.copy()
        self.preview_title.setText("🖼 Uploaded Image")
        self.scan_results.setRowCount(0)

        self.scan_score.setText("Privacy Score : 100")
        self.scan_threat.setText("Threat : LOW")
        self.scan_sensitive.setText("📄 Sensitive : 0")
        self.scan_time.setText("🕒 Last Scan : --")

        self.scan_recommendation.setText(
            "Click 'Scan Text' to analyze the uploaded image."
        )

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb.shape

        bytes_per_line = ch * w

        from PySide6.QtGui import QImage

        qimg = QImage(
            rgb.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(qimg)

        self.scan_preview.setPixmap(
            pixmap.scaled(
                self.scan_preview.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        self.scan_preview.setAlignment(Qt.AlignCenter)

        self.status.setText("Image loaded successfully.")

    def save_safe_image(self):

        if self.protected_scan_image is None:

            self.logs.append("No protected image to save.")
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Protected Image",
            "protected_image.png",
            "PNG Image (*.png);;JPEG Image (*.jpg)"
        )

        if not file_name:
            return

        cv2.imwrite(file_name, self.protected_scan_image)

        self.logs.append(f"Protected image saved:\n{file_name}")
        self.status.setText("Protected image saved.")

    def export_report(self):

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Report",
            "privacy_report.txt",
            "Text File (*.txt)"
        )

        if not file_name:
            return

        with open(file_name, "w", encoding="utf-8") as report:

            report.write("OMPD Privacy Report\n")
            report.write("=" * 35 + "\n\n")

            report.write(f"{self.scan_score.text()}\n")
            report.write(f"{self.scan_threat.text()}\n")
            report.write(f"{self.scan_faces.text()}\n")
            report.write(f"{self.scan_objects.text()}\n")
            report.write(f"{self.scan_sensitive.text()}\n")
            report.write(f"{self.scan_time.text()}\n\n")

            report.write("Recommendation\n")
            report.write("-------------------------\n")
            report.write(
                self.scan_recommendation.toPlainText()
            )

        self.logs.append(
            f"Report exported:\n{file_name}"
        )

        self.status.setText(
            "Report exported."
        )

    def capture_and_protect(self):

        self.capture_button.setEnabled(False)

        try:

            camera_started_here = False

            # ------------------------------------------
            # Ensure camera is available
            # ------------------------------------------

            if self.camera_device.cap is None:

                self.camera_device.start()
                camera_started_here = True

            frame = self.camera_device.get_frame()

            if frame is None:

                self.logs.append(
                    "Unable to capture image."
                )
                return

            frame = frame.copy()

            # ------------------------------------------
            # FACE DETECTION
            # ------------------------------------------

            faces = self.face_detector.detect(frame)

            frame = self.face_detector.blur_faces(
                frame,
                faces,
                self.blur_strength
            )

            # ------------------------------------------
            # YOLO OBJECT DETECTION
            # ------------------------------------------

            detections = self.yolo.detect(frame)

            try:

                frame = self.yolo.blur_objects(
                    frame,
                    detections,
                    self.blur_strength
                )

            except TypeError:

                frame = self.yolo.blur_objects(
                    frame,
                    detections
                )

            # ------------------------------------------
            # OCR
            # ------------------------------------------

            results = self.text_detector.detect(frame)

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

            # ------------------------------------------
            # SHOW IMAGE
            # ------------------------------------------

            self.show_scan_preview(frame)

            # ------------------------------------------
            # UPDATE PRIVACY RISKS TABLE
            # ------------------------------------------

            self.scan_results.setRowCount(0)

            # ---------- Faces ----------

            for _ in faces:

                row = self.scan_results.rowCount()
                self.scan_results.insertRow(row)

                self.scan_results.setItem(
                    row,
                    0,
                    QTableWidgetItem("👤 Face")
                )

                self.scan_results.setItem(
                    row,
                    1,
                    QTableWidgetItem("Human Face")
                )

                self.scan_results.setItem(
                    row,
                    2,
                    QTableWidgetItem("HIGH")
                )

                self.scan_results.setItem(
                    row,
                    3,
                    QTableWidgetItem("100%")
                )

            # ---------- Objects ----------

            for obj in detections:

                label = obj.get("label", "Unknown")
                confidence = obj.get("confidence", 0)

                risk = "LOW"

                if label in self.yolo.sensitive_objects:

                    if self.yolo.sensitive_objects[label]:

                        risk = "HIGH"

                row = self.scan_results.rowCount()
                self.scan_results.insertRow(row)

                self.scan_results.setItem(
                    row,
                    0,
                    QTableWidgetItem("📦 Object")
                )

                self.scan_results.setItem(
                    row,
                    1,
                    QTableWidgetItem(label)
                )

                self.scan_results.setItem(
                    row,
                    2,
                    QTableWidgetItem(risk)
                )

                self.scan_results.setItem(
                    row,
                    3,
                    QTableWidgetItem(
                        f"{confidence*100:.1f}%"
                    )
                )

            # ---------- Sensitive Text ----------

            for bbox, text, confidence in results:

                row = self.scan_results.rowCount()
                self.scan_results.insertRow(row)

                self.scan_results.setItem(
                    row,
                    0,
                    QTableWidgetItem("📄 Sensitive Text")
                )

                self.scan_results.setItem(
                    row,
                    1,
                    QTableWidgetItem(text)
                )

                self.scan_results.setItem(
                    row,
                    2,
                    QTableWidgetItem("HIGH")
                )

                self.scan_results.setItem(
                    row,
                    3,
                    QTableWidgetItem(
                        f"{confidence*100:.1f}%"
                    )
                )

            # ------------------------------------------
            # UPDATE STATS
            # ------------------------------------------

            self.scan_faces.setText(
                f"👤 Faces : {len(faces)}"
            )

            self.scan_objects.setText(
                f"📦 Objects : {len(detections)}"
            )

            self.scan_sensitive.setText(
                f"📄 Sensitive Text : {len(results)}"
            )

            self.scan_time.setText(
                time.strftime(
                    "🕒 Last Scan : %H:%M:%S"
                )
            )

            privacy_score = 100

            privacy_score -= len(faces) * 2
            privacy_score -= len(detections) * 3
            privacy_score -= len(results) * 5

            privacy_score = max(
                0,
                privacy_score
            )

            self.scan_score.setText(
                f"Privacy Score : {privacy_score}"
            )

            if privacy_score >= 85:

                threat = "LOW"

            elif privacy_score >= 60:

                threat = "MEDIUM"

            else:

                threat = "HIGH"

            self.scan_threat.setText(
                f"Threat : {threat}"
            )

            # ------------------------------------------
            # AI Recommendation
            # ------------------------------------------

            recommendation = (
                "Privacy Analysis Report\n\n"

                f"👤 Faces Detected : {len(faces)}\n"

                f"📦 Sensitive Objects : {len(detections)}\n"

                f"📄 Sensitive Text : {len(results)}\n\n"

                f"Privacy Score : {privacy_score}\n"

                f"Threat Level : {threat}\n\n"
            )

            if threat == "LOW":

                recommendation += (
                    "The image contains minimal privacy risks.\n"
                    "Safe to share."
                )

            elif threat == "MEDIUM":

                recommendation += (
                    "Some sensitive information was detected.\n"
                    "Review before sharing."
                )

            else:

                recommendation += (
                    "Multiple privacy risks were detected.\n"
                    "The protected version should be shared instead of the original."
                )

            self.scan_recommendation.setText(
                recommendation
            )

            self.status.setText(
                "Capture & Protect Complete"
            )

            self.logs.append(
                "Capture & Protect completed."
            )

            if camera_started_here:

                self.camera_device.stop()

        except Exception as e:

            self.logs.append(
                f"Capture & Protect Error : {e}"
            )

        finally:

            self.capture_button.setEnabled(True)

    def clear_activity(self):
        pass

    def export_activity(self):
        pass

    def search_activity(self):
        pass

    def filter_activity(self):
        pass

    def refresh_history(self):

        self.history_table.setRowCount(0)

        rows = self.db.get_history()

        self.total_records.setText(
            f"Total Records : {len(rows)}"
        )

        self.today_records.setText(
            f"Today : {len(rows)}"
        )

        self.high_risk.setText(
            "High Risk : --"
        )

        for row_data in rows:

            row = self.history_table.rowCount()

            self.history_table.insertRow(row)

            for column, value in enumerate(row_data):

                if column == 3:

                    value = f"{float(value) * 100:.1f}%"

                self.history_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )

            self.history_table.setItem(
                row,
                4,
                QTableWidgetItem("Blurred")
            )

        if rows:

            self.last_detection.setText(
                f"Last Detection : {rows[0][0]}"
            )

        else:

            self.last_detection.setText(
                "Last Detection : --"
            )

        self.status.setText(
            "History refreshed."
        )

    def get_history(self):

        self.cursor.execute(
            """
            SELECT
                timestamp,
                type,
                label,
                confidence
            FROM detections
            ORDER BY timestamp DESC
            """
        )

        return self.cursor.fetchall()

    def export_history(self):

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export History",
            "history.csv",
            "CSV Files (*.csv)"
        )

        if not file_name:
            return

        with open(file_name, "w", newline="", encoding="utf-8") as file:

            writer = csv.writer(file)

            writer.writerow([
                "Timestamp",
                "Category",
                "Detected Item",
                "Confidence",
                "Action"
            ])

            for row in range(self.history_table.rowCount()):

                values = []

                for column in range(self.history_table.columnCount()):

                    item = self.history_table.item(row, column)

                    values.append("" if item is None else item.text())

                writer.writerow(values)

        self.status.setText("History exported successfully.")

        self.logs.append(
            f"📄 History exported:\n{file_name}"
        )

    def delete_history(self):

        row = self.history_table.currentRow()

        if row == -1:

            self.status.setText(
                "No record selected."
            )
            return

        timestamp = self.history_table.item(row, 0).text()
        event_type = self.history_table.item(row, 1).text()
        label = self.history_table.item(row, 2).text()

        self.db.delete_history_record(
            timestamp,
            event_type,
            label
        )

        self.refresh_history()

        self.logs.append(
            f"Deleted: {label}"
        )

        self.status.setText(
            "Record deleted."
        )

    def clear_history(self):

        self.db.clear_history()

        self.refresh_history()

        self.logs.append(
            "History cleared."
        )

        self.status.setText(
            "History cleared."
        )

    def search_history(self):

        search = self.history_search.text().lower().strip()

        for row in range(self.history_table.rowCount()):

            show = False

            for column in range(self.history_table.columnCount()):

                item = self.history_table.item(row, column)

                if item and search in item.text().lower():

                    show = True
                    break

            self.history_table.setRowHidden(
                row,
                not show
            )

    def filter_history(self):

        selected = self.history_filter.currentText()

        for row in range(self.history_table.rowCount()):

            category_item = self.history_table.item(row, 1)

            if category_item is None:

                continue

            category = category_item.text()

            if selected == "All":

                self.history_table.setRowHidden(row, False)

            elif selected == "Faces":

                self.history_table.setRowHidden(
                    row,
                    category != "Face"
                )

            elif selected == "Objects":

                self.history_table.setRowHidden(
                    row,
                    category != "Sensitive Object"
                )

            elif selected == "Sensitive Text":

                self.history_table.setRowHidden(
                    row,
                    category != "Sensitive Text"
                )

    def save_settings_clicked(self):
        pass

    def reset_settings_clicked(self):
        pass

    def export_database_clicked(self):
        pass

    def backup_database_clicked(self):
        pass

    def clear_database_clicked(self):
        pass

    def open_github(self):
        pass

    def open_license(self):
        pass

    def update_analytics(self):
        pass

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
    # QR / BARCODE BLUR
    # ======================================================

    def toggle_barcode_blur(self):

        self.barcode_enabled = (
            not self.barcode_enabled
        )

        state = (
            "ON"
            if self.barcode_enabled
            else "OFF"
        )

        self.barcode_blur.setText(
            f"Barcode Blur : {state}"
        )

        self.logs.append(
            f"Barcode Blur {state}"
        )

    # ======================================================
    # FILTER OBJECTS
    # ======================================================

    def _filter_results_by_enabled_classes(
        self,
        detections
    ):

        filtered = []

        for detection in detections:

            label = None

            if isinstance(detection, dict):

                label = detection.get(
                    "label",
                    ""
                ).lower()

            elif isinstance(
                detection,
                (list, tuple)
            ):

                for item in detection:

                    if isinstance(item, str):

                        label = item.lower()
                        break

            if (
                label
                and self.sensitive_classes.get(
                    label,
                    False
                )
            ):

                filtered.append(
                    detection
                )

        return filtered

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