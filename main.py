import cv2

from vision.camera import Camera
from vision.yolo_detector import YOLODetector
from vision.face_detector import FaceDetector


camera = Camera()

detector = YOLODetector()

face_detector = FaceDetector()

while True:

    success, frame = camera.read()

    if not success:
        break

    frame = detector.detect_and_blur(frame)

    faces = face_detector.detect(frame)

    frame = face_detector.blur_faces(frame, faces)

    frame = face_detector.draw(frame, faces)

    cv2.imshow(
        "OMPD",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()

cv2.destroyAllWindows()