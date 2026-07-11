import cv2

from vision.camera import Camera
from vision.yolo_detector import YOLODetector
from vision.face_detector import FaceDetector
from vision.text_detector import TextDetector
from database import Database

camera = Camera()

db = Database()
detector = YOLODetector(db=db)

# detector = YOLODetector()

face_detector = FaceDetector()

text_detector = TextDetector()

frame_count = 0
ocr_results = []

while True:

    success, frame = camera.read()

    if not success:
        break
    frame_count += 1

    detections = detector.detect(frame)

    frame = detector.blur_objects(frame, detections)

    faces = face_detector.detect(frame)
    frame = face_detector.blur_faces(frame, faces)

    if frame_count % 15 == 0:
        ocr_results = text_detector.detect(frame)

    frame = text_detector.blur_text(frame, ocr_results)

    frame = detector.draw(frame, detections)
    frame = face_detector.draw(frame, faces)

    cv2.imshow(
        "OMPD",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
db.close()
cv2.destroyAllWindows()