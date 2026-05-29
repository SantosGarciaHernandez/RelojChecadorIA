import cv2
import numpy as np


class FaceDetectionService:
    def __init__(self) -> None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            raise RuntimeError("No se pudo cargar el clasificador Haar Cascade de OpenCV")

    def detect_largest_face(self, frame_bgr: np.ndarray) -> tuple[int, int, int, int] | None:
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
        )
        if len(faces) == 0:
            return None
        return max(faces, key=lambda box: box[2] * box[3])

    def extract_largest_face(self, frame_bgr: np.ndarray) -> tuple[np.ndarray, tuple[int, int, int, int]] | None:
        box = self.detect_largest_face(frame_bgr)
        if not box:
            return None
        x, y, w, h = box
        face = frame_bgr[y : y + h, x : x + w]
        return face, (int(x), int(y), int(w), int(h))
