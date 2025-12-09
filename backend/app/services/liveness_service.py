from fastapi import UploadFile
from app.models.schemas import LivenessResult
import cv2
import numpy as np


async def analyze_liveness(file: UploadFile) -> LivenessResult:
    """
    Analiza la selfie para detectar si hay una persona real (liveness)
    usando heurísticas con OpenCV:
      - detección de rostro
      - tamaño relativo del rostro
      - nitidez de la imagen
      - brillo promedio
    """

    # 1. Leer la imagen desde el UploadFile
    image_bytes = await file.read()
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        return LivenessResult(
            score=0.0,
            isLive=False,
            reason="Invalid image data",
        )

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape[:2]
    img_area = float(h * w)

    # 2. Detectar rostro con Haar Cascade
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
        return LivenessResult(
            score=0.0,
            isLive=False,
            reason="No face detected",
        )

    # Tomamos la cara más grande (por área)
    x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
    face_area = float(fw * fh)
    face_ratio = face_area / img_area  # proporción de la imagen ocupada por la cara

    # 3. Nitidez (varianza del Laplaciano)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    sharpness = laplacian.var()

    # 4. Brillo promedio
    brightness = gray.mean()

    # 5. Normalizar cada métrica a [0,1] de forma empírica
    # Cara: queremos al menos 5% del área y máximo 20%
    face_score = (face_ratio - 0.05) / (0.20 - 0.05)
    face_score = float(max(0.0, min(1.0, face_score)))

    # Nitidez: umbral típico 50–200
    sharp_score = (sharpness - 50.0) / (200.0 - 50.0)
    sharp_score = float(max(0.0, min(1.0, sharp_score)))

    # Brillo: rango aceptable aprox. 40–160
    bright_score = (brightness - 40.0) / (160.0 - 40.0)
    bright_score = float(max(0.0, min(1.0, bright_score)))

    # 6. Score global ponderado
    score = 0.4 * face_score + 0.4 * sharp_score + 0.2 * bright_score
    score = float(max(0.0, min(1.0, score)))

    is_live = score >= 0.7  # umbral de liveness
    reason = None if is_live else "Liveness score below threshold"

    return LivenessResult(
      
        score=score,
        isLive=is_live,
        reason=reason,
    )