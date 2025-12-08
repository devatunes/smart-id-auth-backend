import io
from typing import List, Tuple, Optional
from fastapi import UploadFile
from PIL import Image, ImageFilter
import easyocr
import unicodedata

from app.models.schemas import DocumentOcrResult

# Cargamos el lector una sola vez (caro en tiempo, así no lo repetimos en cada request)
_reader = easyocr.Reader(['es', 'en'], gpu=False)


async def analyze_document_ocr(file: UploadFile) -> DocumentOcrResult:
    """
    Analiza la imagen del documento usando EasyOCR.
    Usa heurísticas específicas para cédula colombiana:
    - Detecta número cercano a la etiqueta NUMERO
    - Detecta apellidos y nombres cerca de APELLIDOS / NOMBRES
    """

    # 1. Leer bytes y preprocesar un poco
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.filter(ImageFilter.SHARPEN)

    # 2. Ejecutar EasyOCR
    # results: [ (bbox, text, confidence), ... ]
    results: List[Tuple] = _reader.readtext(
        image_bytes,
        detail=1,
        paragraph=False,
    )

    texts = [item[1] for item in results]
    confidences = [float(item[2]) for item in results] or [0.0]
    avg_conf = sum(confidences) / len(confidences)

    # 3. Texto con estructura de líneas
    full_text_lines = "\n".join(texts)

    # 4. Extraer número + nombres usando heurísticas basadas en etiquetas
    document_number = _extract_document_number_from_results(results, full_text_lines)
    given_names, surnames = _extract_name_parts_from_results(results, full_text_lines)

    # 5. Estimar calidad de captura
    capture_quality = _estimate_capture_quality(avg_conf, len(results))

    return DocumentOcrResult(
        documentNumber=document_number or "UNKNOWN",
        givenNames=given_names or "UNKNOWN",
        surnames=surnames or "UNKNOWN",
        expiryDate=None,
        ocrConfidence=avg_conf,
        captureQuality=capture_quality,
    )


def _normalize(text: str) -> str:
    """
    Normaliza texto:
    - pasa a mayúsculas
    - quita acentos
    - colapsa espacios
    """
    text = text.upper()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = " ".join(text.split())
    return text


def _extract_document_number_from_results(
    results: List[Tuple], full_text: str
) -> Optional[str]:
    """
    Prioriza:
    1) Buscar número cerca de la etiqueta NUMERO/NRO/NO.
    2) Si falla, busca patrón general de cédula (con o sin puntos).
    """
    import re

    # 1) Uso de contexto con etiqueta NUMERO
    for idx, (_, text, _) in enumerate(results):
        norm = _normalize(text)
        if "NUMERO" in norm or norm.startswith("NO ") or "NRO" in norm:
            # Mirar los siguientes bloques como posibles números
            neighbor_text = ""
            for j in range(1, 4):
                if idx + j < len(results):
                    neighbor_text += " " + results[idx + j][1]

            # primero, con puntos (1.082.997.388)
            match = re.search(r"\b\d{1,3}(?:\.\d{3}){2,3}\b", neighbor_text)
            if match:
                return match.group(0).replace(".", "")

            # luego, número largo sin puntos
            match = re.search(r"\b\d{7,12}\b", neighbor_text)
            if match:
                return match.group(0)

    # 2) Fallback global en todo el texto
    import re

    # con puntos
    match = re.search(r"\b\d{1,3}(?:\.\d{3}){2,3}\b", full_text)
    if match:
        return match.group(0).replace(".", "")

    # sin puntos
    match = re.search(r"\b\d{7,12}\b", full_text)
    if match:
        return match.group(0)

    return None
  

def _extract_name_parts_from_results(
    results: List[Tuple], full_text: str
) -> tuple[Optional[str], Optional[str]]:
    """
    Extrae (givenNames, surnames) usando:
    1) Vecindad de etiquetas APELLIDOS / NOMBRES.
    2) Heurística sobre líneas en mayúsculas sin dígitos.
    """
    import re

    lines = [l.strip() for l in full_text.splitlines() if l.strip()]

    # -------- 1) Intento basado en etiquetas APELLIDOS / NOMBRES --------
    surnames = None
    given_names = None

    norm_lines = [_normalize(l) for l in lines]

    # Buscar apellidos
    for idx, ln in enumerate(norm_lines):
        if "APELLIDOS" in ln or "APELLIDO" in ln:
            # tomar la siguiente línea con 2+ palabras, sin dígitos, en mayúsculas
            for j in range(idx + 1, min(idx + 4, len(lines))):
                candidate = lines[j].strip()
                cand_norm = _normalize(candidate)
                if not re.match(r"^[A-ZÁÉÍÓÚÑ ]+$", candidate):
                    continue
                if any(ch.isdigit() for ch in candidate):
                    continue
                if len(candidate.split()) < 2:
                    continue
                surnames = " ".join(candidate.split())
                break
            if surnames:
                break

    # Buscar nombres
    for idx, ln in enumerate(norm_lines):
        if "NOMBRES" in ln or "NOMBRE" in ln:
            for j in range(idx + 1, min(idx + 4, len(lines))):
                candidate = lines[j].strip()
                cand_norm = _normalize(candidate)
                if not re.match(r"^[A-ZÁÉÍÓÚÑ ]+$", candidate):
                    continue
                if any(ch.isdigit() for ch in candidate):
                    continue
                if len(candidate.split()) < 1:
                    continue
                given_names = " ".join(candidate.split())
                break
            if given_names:
                break

    # Si ya conseguimos ambos por contexto, devolvemos
    if given_names or surnames:
        return given_names, surnames

    # -------- 2) Fallback heurístico usando solo líneas en mayúsculas --------

    BLOCK_WORDS = {
        "REPUBLICA",
        "COLOMBIA",
        "REPUBLICA DE COLOMBIA",
        "IDENTIFICACION PERSONAL",
        "IDENTIFICACION",
        "PERSONAL",
        "CEDULA",
        "CIUDADANIA",
        "CEDULA DE CIUDADANIA",
        "NUMERO",
        "FIRMA",
        "DE",
        "LA",
        "DEL",
    }

    candidates = []
    for line in lines:
        clean = line.replace(":", "").strip()

        if not re.match(r"^[A-ZÁÉÍÓÚÑ ]+$", clean):
            continue
        if any(ch.isdigit() for ch in clean):
            continue

        clean = re.sub(r"\s+", " ", clean)

        if _normalize(clean) in {_normalize(b) for b in BLOCK_WORDS}:
            continue

        if len(clean.split()) < 2:
            continue

        candidates.append(clean)

    if not candidates:
        return None, None

    # Ordenamos por cantidad de palabras (la más corta suele ser apellidos)
    candidates_sorted = sorted(candidates, key=lambda s: len(s.split()))

    if len(candidates_sorted) >= 2:
        surnames = candidates_sorted[0]
        given_names = candidates_sorted[1]
        return given_names, surnames

    only = candidates_sorted[0]
    return only, None


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