import base64
from typing import Tuple

import cv2
import numpy as np
from PIL import Image


def decode_base64_image(image_base64: str) -> np.ndarray:
    """Convierte base64 o data URL a imagen OpenCV BGR."""
    if "," in image_base64:
        image_base64 = image_base64.split(",", 1)[1]

    image_bytes = base64.b64decode(image_base64)
    return decode_image_bytes(image_bytes)


def decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    """Convierte bytes de imagen a OpenCV BGR."""
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("La imagen no pudo decodificarse")
    return image


def image_to_jpeg_bytes(image_bgr: np.ndarray) -> bytes:
    ok, buffer = cv2.imencode(".jpg", image_bgr)
    if not ok:
        raise ValueError("No se pudo convertir la imagen a JPG")
    return buffer.tobytes()


def preprocess_face(
    face_bgr: np.ndarray,
    target_size: Tuple[int, int],
    channels: int = 3,
    normalize: bool = False,
) -> np.ndarray:
    """
    Prepara una cara ya recortada para Keras.

    Importante para este proyecto:
    - El frontend manda la cara recortada.
    - El modelo espera 128x128x3.
    - El modelo ya incluye Rescaling(1./255), por eso normalize=False por defecto.
    """
    width, height = target_size
    resized = cv2.resize(face_bgr, (width, height), interpolation=cv2.INTER_AREA)

    if channels == 1:
        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        resized = np.expand_dims(resized, axis=-1)
    else:
        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

    tensor = resized.astype("float32")
    if normalize:
        tensor = tensor / 255.0

    return np.expand_dims(tensor, axis=0)


def preprocess_pil_image(
    image: Image.Image,
    target_size: Tuple[int, int],
    channels: int = 3,
    normalize: bool = False,
) -> np.ndarray:
    """Alternativa de preprocesamiento usando PIL, útil para pruebas unitarias."""
    width, height = target_size
    image = image.convert("RGB" if channels == 3 else "L")
    image = image.resize((width, height))
    array = np.asarray(image).astype("float32")

    if channels == 1:
        array = np.expand_dims(array, axis=-1)

    if normalize:
        array = array / 255.0

    return np.expand_dims(array, axis=0)
