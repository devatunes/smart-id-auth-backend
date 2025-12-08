from fastapi import UploadFile
from app.models.schemas import LivenessResult


async def analyze_liveness(file: UploadFile) -> LivenessResult:
    """
    Analiza la selfie para detectar si hay una persona real (liveness).
    Por ahora es un STUB: devuelve un resultado simulado.
    Más adelante aquí integraremos un modelo real de anti-spoofing
    (por ejemplo, basado en parpadeo o acercamiento).
    """

    # TODO: Leer bytes, extraer rostro, aplicar modelo de liveness.
    # image_bytes = await file.read()
    # ... modelo real de liveness ...

    # Resultado simulado "sano":
    score = 0.93
    is_live = score >= 0.8

    return LivenessResult(
        score=score,
        isLive=is_live,
        reason=None if is_live else "Low liveness score",
    )