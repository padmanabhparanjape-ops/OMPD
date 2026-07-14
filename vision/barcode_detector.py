import cv2


class QRBarcodeDetector:
    """
    Detects QR codes and barcodes in a frame using OpenCV's
    built-in detectors (no external native dependencies),
    and provides a blur utility to obscure them.
    """

    def __init__(self):
        self.qr_detector = cv2.QRCodeDetector()

        try:
            self.barcode_detector = cv2.barcode_BarcodeDetector()
            self.barcode_supported = True
        except Exception:
            self.barcode_detector = None
            self.barcode_supported = False

    def detect(self, frame):
        """
        Returns a list of dicts:
        {
            "type": "QRCODE" / "BARCODE",
            "data": decoded string,
            "box": (x, y, w, h)
        }
        """
        detections = []

        detections.extend(self._detect_qr(frame))

        if self.barcode_supported:
            detections.extend(self._detect_barcode(frame))

        return detections

    def _detect_qr(self, frame):

        results = []

        try:
            ok, decoded_info, points, _ = (
                self.qr_detector.detectAndDecodeMulti(frame)
            )
        except Exception:
            return results

        if not ok or points is None:
            return results

        for i, quad in enumerate(points):

            box = self._quad_to_box(quad)

            if box is None:
                continue

            data = ""
            if decoded_info and i < len(decoded_info):
                data = decoded_info[i]

            results.append({
                "type": "QRCODE",
                "data": data,
                "box": box
            })

        return results

    def _detect_barcode(self, frame):

        results = []

        try:
            ok, decoded_info, decoded_type, points = (
                self.barcode_detector.detectAndDecode(frame)
            )
        except Exception:
            return results

        if not ok or points is None:
            return results

        for i, quad in enumerate(points):

            box = self._quad_to_box(quad)

            if box is None:
                continue

            data = ""
            if decoded_info and i < len(decoded_info):
                data = decoded_info[i]

            btype = "BARCODE"
            if decoded_type and i < len(decoded_type):
                btype = str(decoded_type[i])

            results.append({
                "type": btype,
                "data": data,
                "box": box
            })

        return results

    def _quad_to_box(self, quad):
        """
        Converts a 4-point polygon (as returned by OpenCV) into
        an axis-aligned (x, y, w, h) box.
        """
        try:
            pts = quad.reshape(-1, 2)
        except Exception:
            return None

        if pts.shape[0] == 0:
            return None

        xs = pts[:, 0]
        ys = pts[:, 1]

        x = int(xs.min())
        y = int(ys.min())
        w = int(xs.max() - xs.min())
        h = int(ys.max() - ys.min())

        if w <= 0 or h <= 0:
            return None

        return (x, y, w, h)

    def blur_codes(self, frame, detections, blur_strength=15):
        """
        Blurs the region of every detected QR code / barcode.
        """
        if not detections:
            return frame

        k = max(1, int(blur_strength))
        if k % 2 == 0:
            k += 1

        for det in detections:
            x, y, w, h = det.get("box", (0, 0, 0, 0))

            if w <= 0 or h <= 0:
                continue

            x = max(0, x)
            y = max(0, y)
            x2 = min(frame.shape[1], x + w)
            y2 = min(frame.shape[0], y + h)

            roi = frame[y:y2, x:x2]

            if roi.size == 0:
                continue

            blurred = cv2.GaussianBlur(roi, (k, k), 0)
            frame[y:y2, x:x2] = blurred

        return frame