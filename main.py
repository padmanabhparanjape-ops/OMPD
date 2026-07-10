import cv2

from vision.camera import Camera
from vision.yolo_detector import YOLODetector


camera = Camera()

detector = YOLODetector()

while True:

    success, frame = camera.read()

    if not success:
        break

    detections = detector.detect(frame)

    frame = detector.draw(
        frame,
        detections
    )

    cv2.imshow(
        "OmniGuardian Lite",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()

cv2.destroyAllWindows()