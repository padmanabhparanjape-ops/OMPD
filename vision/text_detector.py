import cv2
from config.device import GPU_ENABLED
import easyocr
import re


class TextDetector:

    def __init__(self, languages=["en"]):

        self.reader = easyocr.Reader(
            languages,
            gpu=GPU_ENABLED
        )

        print(f"EasyOCR running on: {'GPU' if GPU_ENABLED else 'CPU'}")

    def detect(self, frame):
        """
        Detect text in the frame.
        Normalize OCR output.
        """

        results = self.reader.readtext(frame)

        normalized_results = []

        for bbox, text, confidence in results:

            text = text.strip()

            # Fix common OCR mistakes
            text = text.replace("_", ".")
            text = text.replace(",", ".")
            text = text.replace(";", ".")
            text = " ".join(text.split())

            normalized_results.append(
                (bbox, text, confidence)
            )

        return normalized_results
    
    def is_sensitive(self, text):

        # -----------------------------
        # Normalize OCR output
        # -----------------------------

        text = text.strip()

        text = text.replace(",", ".")
        text = text.replace(";", ".")
        text = text.replace(" ", "")

        # =====================================================
        # Email
        # =====================================================

        if re.search(
            r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
            text,
            re.IGNORECASE
        ):
            return True

        # =====================================================
        # Phone Number
        # =====================================================

        digits = re.sub(r"\D", "", text)

        # 10-digit Indian number

        if len(digits) == 10:
            return True

        # +91XXXXXXXXXX

        if len(digits) == 12 and digits.startswith("91"):
            return True

        # =====================================================
        # Aadhaar
        # =====================================================

        if re.fullmatch(r"\d{12}", digits):
            return True

        # =====================================================
        # PAN
        # =====================================================

        if re.fullmatch(
            r"[A-Z]{5}[0-9]{4}[A-Z]",
            text.upper()
        ):
            return True

        # =====================================================
        # Credit / Debit Card
        # =====================================================

        if 13 <= len(digits) <= 19:
            return True

        # =====================================================
        # UPI ID
        # =====================================================

        if re.search(
            r"[A-Za-z0-9.\-_]{2,}@[A-Za-z]{2,}",
            text,
            re.IGNORECASE
        ):
            return True

        # =====================================================
        # IFSC
        # =====================================================

        if re.fullmatch(
            r"[A-Z]{4}0[A-Z0-9]{6}",
            text.upper()
        ):
            return True

        # =====================================================
        # Passport (Indian)
        # =====================================================

        if re.fullmatch(
            r"[A-Z][0-9]{7}",
            text.upper()
        ):
            return True

        # =====================================================
        # Driving Licence (India)
        # =====================================================

        if re.fullmatch(
            r"[A-Z]{2}[0-9]{2}[0-9]{11,13}",
            text.upper()
        ):
            return True

        # =====================================================
        # Voter ID (EPIC)
        # =====================================================

        if re.fullmatch(
            r"[A-Z]{3}[0-9]{7}",
            text.upper()
        ):
            return True

        # =====================================================
        # URL
        # =====================================================

        if re.search(
            r"(https?://|www\.)",
            text,
            re.IGNORECASE
        ):
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