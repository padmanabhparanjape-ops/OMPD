import cv2


class Camera:

    def __init__(
        self,
        camera_index=0,
        width=640,
        height=480
    ):

        self.camera_index = camera_index

        self.width = width
        self.height = height

        self.cap = None

    def start(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_index)

            self.cap.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                self.width
            )

            self.cap.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                self.height
            )

        if not self.cap.isOpened():
            raise Exception("Could not open webcam.")

    def get_frame(self):
        if self.cap is None:
            return None

        ret, frame = self.cap.read()

        if not ret:
            return None

        return frame

    def stop(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None