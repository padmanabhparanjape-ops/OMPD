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
        print("Face detections:", len(detections))
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

    def blur_faces(self, frame, detections, blur_level=51):
        """
        Blur all detected faces.

        Args:
            frame: Original frame
            detections: Face detections from detect()
            blur_level: Must be an odd number (31, 51, 71...)

        Returns:
            Frame with blurred faces.
        """

        for detection in detections:

            x1, y1, x2, y2 = detection["bbox"]

            # Prevent coordinates from going outside the image
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(frame.shape[1], x2)
            y2 = min(frame.shape[0], y2)

            face = frame[y1:y2, x1:x2]

            if face.size == 0:
                continue

            blurred_face = cv2.GaussianBlur(
                face,
                (blur_level, blur_level),
                0
            )

            frame[y1:y2, x1:x2] = blurred_face

        return frame
        