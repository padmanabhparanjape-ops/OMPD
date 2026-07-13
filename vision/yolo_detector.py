import cv2
from ultralytics import YOLO
from config.config import SENSITIVE_OBJECTS
import time

class YOLODetector:
    def __init__(self, model_path="models/yolov8n.pt", conf=0.5,db=None):
        self.model = YOLO(model_path)
        self.conf = conf
        self.db = db
        self.last_logged = {}

        # Objects to blur
        self.sensitive_objects = SENSITIVE_OBJECTS.copy()
    
    def detect(self, frame):
        return self.model(frame, verbose=False)
    
    def blur_objects(self, frame, results):

        for result in results:

            boxes = result.boxes

            for box in boxes:

                confidence = float(box.conf[0])

                if confidence < self.conf:
                    continue

                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]

                # -----------------------------------------
                # Ignore disabled object types
                # -----------------------------------------

                enabled = self.sensitive_objects.get(label, False)

                if not enabled:
                    continue

                # -----------------------------------------
                # Database Logging
                # -----------------------------------------

                if self.db:

                    current_time = time.time()

                    if (
                        label not in self.last_logged
                        or current_time - self.last_logged[label] > 1
                    ):

                        self.db.log_detection(
                            "Object",
                            label,
                            confidence
                        )

                        self.last_logged[label] = current_time

                # -----------------------------------------
                # Bounding Box
                # -----------------------------------------

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                h, w = frame.shape[:2]

                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w, x2)
                y2 = min(h, y2)

                roi = frame[y1:y2, x1:x2]

                if roi.size == 0:
                    continue

                blur = cv2.GaussianBlur(
                    roi,
                    (51, 51),
                    30
                )

                frame[y1:y2, x1:x2] = blur

        return frame
    
    def draw(self, frame, results):

        for result in results:
            boxes = result.boxes

            for box in boxes:

                confidence = float(box.conf[0])

                if confidence < self.conf:
                    continue

                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                h, w = frame.shape[:2]
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w, x2)
                y2 = min(h, y2)

                enabled = self.sensitive_objects.get(label, False)

                if not enabled:
                    continue

                color = (0, 0, 255)

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    color,
                    2
                )

                text = f"{label} {confidence:.2f}"

                cv2.putText(
                    frame,
                    text,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )

        return frame