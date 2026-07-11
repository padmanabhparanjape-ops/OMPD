import cv2


class Camera:

    def __init__(self):
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(0)

    def get_frame(self):

        if self.cap is None:
            return None

        success, frame = self.cap.read()

        if success:
            return frame

        return None

    def stop(self):

        if self.cap:
            self.cap.release()
            self.cap = None