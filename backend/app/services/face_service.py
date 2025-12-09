# app/services/face_service.py

from typing import Optional
import cv2
import numpy as np


def _decode_image(image_bytes: bytes) -> Optional[np.ndarray]:
    """
    Decodifica bytes de imagen a un arreglo BGR de OpenCV.
    """
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img


def _detect_largest_face_gray(img: np.ndarray) -> Optional[np.ndarray]:
    """
    Detecta el rostro más grande en la imagen y devuelve el recorte en escala de grises.
    Si no se detecta rostro, devuelve None.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60),
    )

    if len(faces) == 0:
        return None

    # Cara más grande
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face_gray = gray[y : y + h, x : x + w]
    return face_gray


def extract_face_descriptor(image_bytes: bytes) -> Optional[list[float]]:
    """
    Extrae un descriptor de rostro simple:
      - detecta rostro
      - recorta
      - redimensiona a 64x64
      - aplana y normaliza (L2)

    Devuelve una lista de floats (vector) o None si no hay rostro.
    """
    img = _decode_image(image_bytes)
    if img is None:
        return None

    face_gray = _detect_largest_face_gray(img)
    if face_gray is None:
        return None

    face_resized = cv2.resize(face_gray, (64, 64))
    vec = face_resized.flatten().astype("float32")
    norm = np.linalg.norm(vec)
    if norm == 0.0:
        return None

    vec /= norm  # normalizar
    return vec.tolist()


def compute_face_similarity(desc1: list[float], desc2: list[float]) -> float:
    """
    Calcula similitud de coseno entre dos descriptores y la normaliza a [0,1].
    0 = nada parecido, 1 = idéntico.
    """
    v1 = np.array(desc1, dtype="float32")
    v2 = np.array(desc2, dtype="float32")

    denom = float(np.linalg.norm(v1) * np.linalg.norm(v2))
    if denom == 0.0:
        return 0.0

    cos_sim = float(np.dot(v1, v2) / denom)  # [-1, 1]
    score = (cos_sim + 1.0) / 2.0            # [0, 1]
    return max(0.0, min(1.0, score))