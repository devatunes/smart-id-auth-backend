from fastapi import UploadFile
from app.models.schemas import LivenessResult
import cv2
import numpy as np
from typing import Tuple


def _heuristic_liveness_score(
    gray: np.ndarray,
    face_box: Tuple[int, int, int, int],
    img_area: float,
) -> tuple[float, list[str]]:
    """
    Calcula un score heurístico 0-1 usando:
      - tamaño relativo del rostro
      - nitidez (Laplacian)
      - brillo promedio

    Devuelve:
      - score (0-1)
      - lista de razones de mala calidad (si aplica)
    """
    x, y, fw, fh = face_box

    # Área de la cara vs área total
    face_area = float(fw * fh)
    face_ratio = face_area / img_area if img_area > 0 else 0.0

    # Nitidez (varianza del Laplaciano)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    sharpness = laplacian.var()

    # Brillo promedio
    brightness = gray.mean()

    # Normalizar cada métrica a [0,1] de forma empírica
    # Cara: queremos al menos 5% del área y máximo ~20%
    face_score = (face_ratio - 0.05) / (0.20 - 0.05)
    face_score = float(max(0.0, min(1.0, face_score)))

    # Nitidez: umbral típico 50–200
    sharp_score = (sharpness - 50.0) / (200.0 - 50.0)
    sharp_score = float(max(0.0, min(1.0, sharp_score)))

    # Brillo: rango aceptable aprox. 40–160
    bright_score = (brightness - 40.0) / (160.0 - 40.0)
    bright_score = float(max(0.0, min(1.0, bright_score)))

    # Score global ponderado (igual que antes)
    score = 0.4 * face_score + 0.4 * sharp_score + 0.2 * bright_score
    score = float(max(0.0, min(1.0, score)))

    # Razones de mala calidad
    reasons: list[str] = []
    if face_score < 0.5:
        reasons.append("Face size not ideal in the frame")
    if sharp_score < 0.5:
        reasons.append("Image too blurry")
    if bright_score < 0.5:
        reasons.append("Lighting conditions are poor")

    return score, reasons


def _model_antispoof_score(face_img: np.ndarray) -> float:
    """
    Hook para un modelo de anti-spoofing basado en IA (CNN / ONNX).

    Devuelve un score 0-1 donde:
      - 1.0 = claramente real
      - 0.0 = claramente spoof

    Por ahora es un STUB: se puede dejar un valor fijo alto o
    una pequeña heurística adicional. Más adelante aquí se cargará
    un modelo real con PyTorch u ONNX Runtime.
    """
    # TODO: reemplazar por inferencia real de modelo CNN / ONNX.
    # Ejemplo futuro:
    #   - preprocesar face_img
    #   - pasar por modelo
    #   - obtener probabilidad de "real"
    #
    # Por ahora devolvemos un valor fijo razonablemente alto
    # para no romper el comportamiento actual.
    return 0.85


async def analyze_liveness(file: UploadFile) -> LivenessResult:
    """
    Analiza la selfie para detectar si hay una persona real (liveness),
    combinando:

      1) Heurísticas de calidad (OpenCV):
         - detección de rostro
         - tamaño relativo de la cara
         - nitidez
         - brillo

      2) Hook para modelo de anti-spoof (CNN/ONNX) sobre el rostro recortado.

    Retorna:
      - score 0-1
      - isLive (True/False)
      - reason con detalles en caso de rechazo
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

    # 2. Detectar rostro con Haar Cascade (igual que antes)
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
    face_box = (x, y, fw, fh)
    face_img = img[y:y + fh, x:x + fw]

    # 3. Score heurístico (lo que ya tenías, encapsulado)
    quality_score, quality_reasons = _heuristic_liveness_score(
        gray=gray,
        face_box=face_box,
        img_area=img_area,
    )

    # 4. Score del modelo anti-spoof (por ahora stub)
    model_score = _model_antispoof_score(face_img)

    # 5. Combinar scores
    #    Pesos 50/50 entre calidad y modelo (se pueden tunear)
    final_score = 0.5 * quality_score + 0.5 * model_score
    final_score = float(max(0.0, min(1.0, final_score)))

    # Umbral de liveness un poco más exigente
    LIVENESS_THRESHOLD = 0.75
    is_live = final_score >= LIVENESS_THRESHOLD

    if is_live:
        reason = None
    else:
        reasons = list(quality_reasons)
        if model_score < 0.7:
            reasons.append("Anti-spoof model indicates spoof risk")
        if not reasons:
            reasons.append("Liveness score below threshold")
        reason = "; ".join(reasons)

    return LivenessResult(
        score=final_score,
        isLive=is_live,
        reason=reason,
    )