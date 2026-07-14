import cv2
from config.device import DEVICE,GPU_ENABLED
from ultralytics import YOLO
from config.config import SENSITIVE_OBJECTS
import torch

class YOLODetector:
    def __init__(self, model_path="models/yolov8n.pt", conf=0.5,db=None):
        self.model = YOLO(model_path)
        self.class_names = self.model.names
        self.model.to(DEVICE)
        self.conf = conf
        self.db = db
        self.last_logged = {}

        # Objects to blur
        self.sensitive_objects = SENSITIVE_OBJECTS.copy()
    
    def detect(self, frame):

        with torch.inference_mode():

            results = self.model(
                frame,
                device=DEVICE,
                half=GPU_ENABLED,
                verbose=False
            )

        detections = []

        for result in results:

            for box in result.boxes:

                confidence = float(box.conf[0])

                if confidence < self.conf:
                    continue

                cls_id = int(box.cls[0])

                label = self.class_names[cls_id]

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                detections.append({
                    "label": label,
                    "confidence": confidence,
                    "bbox": (x1, y1, x2, y2)
                })

        return detections
    
    def blur_objects(
        self,
        frame,
        detections,
        blur_strength=31
    ):

        for obj in detections:

            label = obj["label"]

            confidence = obj["confidence"]

            if not self.sensitive_objects.get(label, False):
                continue

            x1, y1, x2, y2 = obj["bbox"]

            h, w = frame.shape[:2]

            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(w, x2)
            y2 = min(h, y2)

            roi = frame[y1:y2, x1:x2]

            if roi.size == 0:
                continue

            blur = max(3, int(blur_strength))

            if blur % 2 == 0:
                blur += 1

            roi = cv2.GaussianBlur(
                roi,
                (blur, blur),
                0
            )

            frame[y1:y2, x1:x2] = roi

        return frame
    
    def draw(self, frame, results):

        for result in results:
            boxes = result.boxes

            for box in boxes:

                confidence = float(box.conf[0])

                if confidence < self.conf:
                    continue

                cls_id = int(box.cls[0])
                label = self.class_names[cls_id]

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