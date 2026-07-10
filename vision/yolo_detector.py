
from ultralytics import YOLO


class YOLODetector:

    def __init__(
        self,
        model_name="yolov8n.pt",
        confidence=0.5
    ):

        self.model = YOLO(model_name)
        self.confidence = confidence

        self.sensitive_objects = {
            "person",
            "cell phone",
            "laptop",
            "keyboard",
            "mouse",
            "book",
            "tv",
            "remote",
            "monitor"
        }

    def detect(self, frame):

        detections = []

        results = self.model(
            frame,
            conf=self.confidence,
            verbose=False
        )

        for result in results:

            for box in result.boxes:

                class_id = int(box.cls[0])

                label = self.model.names[class_id]

                confidence = float(box.conf[0])

                if label not in self.sensitive_objects:
                    continue

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                detections.append(
                    {
                        "label": label,
                        "confidence": confidence,
                        "bbox": (
                            x1,
                            y1,
                            x2,
                            y2
                        )
                    }
                )

        return detections

    def draw(self, frame, detections):

        import cv2

        for detection in detections:

            x1, y1, x2, y2 = detection["bbox"]

            label = detection["label"]

            confidence = detection["confidence"]

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            text = f"{label} {confidence:.2f}"

            cv2.putText(
                frame,
                text,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        return frame