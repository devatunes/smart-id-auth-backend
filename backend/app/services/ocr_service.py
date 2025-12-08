from fastapi import UploadFile
from app.models.schemas import DocumentOcrResult

import io
from typing import List, Tuple

import easyocr
from PIL import Image, ImageFilter


# Cargamos el lector una sola vez (caro en tiempo, así no lo repetimos en cada request)
_reader = easyocr.Reader(['es', 'en'], gpu=False)


async def analyze_document_ocr(file: UploadFile) -> DocumentOcrResult:
    """
    Analiza la imagen del documento usando EasyOCR.
    - Lee el texto de la imagen.
    - Intenta extraer número de documento y nombre.
    - Estima calidad de captura de forma simple.
    """

    # 1. Leer bytes del archivo
    image_bytes = await file.read()

    # 2. Abrir imagen con PIL para posibles preprocesos
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # (Opcional simple) Filtrado ligero para mejorar legibilidad
    image = image.filter(ImageFilter.SHARPEN)

    # 3. Ejecutar EasyOCR
    #    resultado: lista de [ [bbox], text, confidence ]
    results: List[Tuple] = _reader.readtext(
        image_bytes,  # también podría ser el path o np.array
        detail=1,
        paragraph=False,
    )

    # 4. Extraer textos y promediar confianza
    texts = [item[1] for item in results]
    confidences = [float(item[2]) for item in results] or [0.0]
    avg_conf = sum(confidences) / len(confidences)

    full_text = " ".join(texts)

    # 5. Heurísticas simples para número de documento y nombre
    # Nota: esto depende del formato del documento, aquí usamos algo genérico.
    document_number = _extract_document_number(full_text)
    full_name = _extract_full_name(full_text)

    # 6. Estimar calidad de captura
    capture_quality = _estimate_capture_quality(avg_conf, results)

    return DocumentOcrResult(
        documentNumber=document_number or "UNKNOWN",
        fullName=full_name or "UNKNOWN",
        expiryDate=None,  # esto lo podemos trabajar luego con regex en full_text
        ocrConfidence=avg_conf,
        captureQuality=capture_quality,
    )


def _extract_document_number(text: str) -> str | None:
    """
    Intenta extraer un número de documento simple:
    - Secuencia de 7 a 12 dígitos (puedes ajustar según país).
    """
    import re

    match = re.search(r"\b\d{7,12}\b", text)
    return match.group(0) if match else None


def _extract_full_name(text: str) -> str | None:
    """
    Heurística súper simple para nombre:
    - Busca una línea con varias palabras en mayúscula.
    - Esto se puede ajustar a tu formato de documento.
    """
    candidates = []
    for line in text.splitlines():
        clean = line.strip()
        if len(clean.split()) >= 2 and clean.isupper():
            candidates.append(clean)

    # devuelve la primera candidata o None
    return candidates[0] if candidates else None


def _estimate_capture_quality(avg_conf: float, results_len: int) -> str:
    """
    Estima una calidad de captura simple usando:
    - confianza OCR promedio
    - cantidad de bloques de texto detectados
    """

    if results_len == 0:
        return "OUT_OF_FRAME"

    if avg_conf < 0.4:
        return "BLURRY"

    if results_len < 3:
        return "PARTIAL"

    return "GOOD"