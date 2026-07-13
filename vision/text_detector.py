import cv2
import easyocr
import re


class TextDetector:

    def __init__(self, languages=["en"], gpu=False):
        self.reader = easyocr.Reader(languages, gpu=gpu)

    def detect(self, frame):
        """
        Detect text in the frame.
        Returns EasyOCR results.
        """
        return self.reader.readtext(frame)
    
    def is_sensitive(self, text):

        text = text.strip()

        # Email
        if re.fullmatch(r'[\w\.-]+@[\w\.-]+\.\w+', text):
            return True

        # Phone number (10 digits)
        if re.fullmatch(r'\d{10}', text):
            return True

        # Aadhaar (12 digits)
        if re.fullmatch(r'\d{12}', text):
            return True

        # PAN
        if re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]', text):
            return True

        return False

    def blur_text(self, frame, results,blur_strength):
        """
        Blur all detected text regions.
        """

        for result in results:

            bbox, text, confidence = result
           
            if not self.is_sensitive(text):
               continue

            x_coords = [int(point[0]) for point in bbox]
            y_coords = [int(point[1]) for point in bbox]

            x1 = max(0, min(x_coords))
            y1 = max(0, min(y_coords))
            x2 = min(frame.shape[1], max(x_coords))
            y2 = min(frame.shape[0], max(y_coords))

            roi = frame[y1:y2, x1:x2]
           

            if roi.size != 0:
                blur = max(3, int(blur_strength))

                if blur % 2 == 0:
                    blur += 1

                roi = cv2.GaussianBlur(roi, (blur, blur), 0)
                frame[y1:y2, x1:x2] = roi

        return frame

    def draw(self, frame, results):

        for result in results:

            bbox, text, confidence = result

            pts = [(int(x), int(y)) for x, y in bbox]

            cv2.line(frame, pts[0], pts[1], (0,255,0),2)
            cv2.line(frame, pts[1], pts[2], (0,255,0),2)
            cv2.line(frame, pts[2], pts[3], (0,255,0),2)
            cv2.line(frame, pts[3], pts[0], (0,255,0),2)

            cv2.putText(
                frame,
                text,
                (pts[0][0], pts[0][1]-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,255,0),
                2
            )

        return frame