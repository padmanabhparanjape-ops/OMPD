from camera import Camera
import cv2


cam = Camera()
cam.start()


while True:

    frame = cam.get_frame()

    if frame is not None:
        cv2.imshow("Test Camera", frame)


    if cv2.waitKey(1) == ord('q'):
        break


cam.stop()
cv2.destroyAllWindows()