import cv2
import mediapipe as mp


class FaceDetector:

    def __init__(self, min_detection_confidence=0.5):

        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=min_detection_confidence
        )

    def detect(self, frame):

        detections = []

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.face_detection.process(rgb)

        if results.detections:

            h, w, _ = frame.shape

            for detection in results.detections:

                bbox = detection.location_data.relative_bounding_box

                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)

                detections.append({
                    "label": "face",
                    "confidence": detection.score[0],
                    "bbox": (
                        x,
                        y,
                        x + width,
                        y + height
                    )
                })

        return detections

    def draw(self, frame, detections):

        for detection in detections:

            x1, y1, x2, y2 = detection["bbox"]

            confidence = detection["confidence"]

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                2
            )

            cv2.putText(
                frame,
                f"Face {confidence:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )

        return frame