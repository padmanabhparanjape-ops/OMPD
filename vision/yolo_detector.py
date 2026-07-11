import cv2
from ultralytics import YOLO
from config.config import SENSITIVE_OBJECTS

class YOLODetector:
    def __init__(self, model_path="models/yolov8n.pt", conf=0.5):
        self.model = YOLO(model_path)
        self.conf = conf

        # Objects to blur
        self.sensitive_objects = SENSITIVE_OBJECTS
    
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

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                h, w = frame.shape[:2]
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w, x2)
                y2 = min(h, y2)

                if label in self.sensitive_objects:

                    roi = frame[y1:y2, x1:x2]

                    if roi.size != 0:
                        blur = cv2.GaussianBlur(roi, (51, 51), 30)
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

                if label in self.sensitive_objects:
                    color = (0, 0, 255)      # Red
                else:
                    color = (0, 255, 0)      # Green

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

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