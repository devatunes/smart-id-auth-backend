from typing import Optional

from app.models.schemas import DecisionResult
from app.services.session_service import update_session
from app.helpers.session_helper import ensure_session


def evaluate_authentication(session_id: str) -> DecisionResult:
    """
    Evalúa la sesión usando:
    - Validación del documento
    - OCR (confianza + calidad)
    - Liveness de la selfie
    - Face match entre rostro del documento y selfie

    Devuelve una decisión final y actualiza la sesión.
    Lanza SessionNotFoundError si la sesión no existe.
    """

    # 1) Validar / obtener sesión (lanza SessionNotFoundError si no existe)
    session = ensure_session(session_id)

    reasons: list[str] = []

    # -------------------------
    # 1) Validación de flujos
    # -------------------------
    if not getattr(session, "documentProcessed", False):
        reasons.append("Document not processed")

    if not getattr(session, "selfieProcessed", False):
        reasons.append("Selfie not processed")

    # -------------------------
    # 2) Validación de documento
    # -------------------------
    document_valid: Optional[bool] = getattr(session, "documentValid", None)
    document_validation_reason: Optional[str] = getattr(
        session, "documentValidationReason", None
    )

    if document_valid is False:
        reasons.append(
            f"Document invalid: {document_validation_reason or 'Unknown reason'}"
        )

    # -------------------------
    # 3) OCR y calidad
    # -------------------------
    ocr_conf: Optional[float] = getattr(session, "ocrConfidence", None)
    capture_quality: Optional[str] = getattr(session, "captureQuality", None)

    if ocr_conf is not None and ocr_conf < 0.6:
        reasons.append("Low OCR confidence")

    if capture_quality in ("BLURRY", "PARTIAL", "OUT_OF_FRAME"):
        reasons.append(f"Capture quality is {capture_quality}")

    # -------------------------
    # 4) Liveness (umbral 0.75)
    # -------------------------
    liveness_score: Optional[float] = getattr(session, "livenessScore", None)
    liveness_reason: Optional[str] = getattr(session, "livenessReason", None)

    if liveness_score is None:
        reasons.append("Liveness not evaluated")
    elif liveness_score < 0.75:  # 👈 antes 0.8
        if liveness_reason:
            reasons.append(f"Liveness score too low: {liveness_reason}")
        else:
            reasons.append("Liveness score too low")

    # -------------------------
    # 5) Face match
    # -------------------------
    face_match_score: Optional[float] = getattr(session, "faceMatchScore", None)

    # Solo penalizamos si sabemos que se evaluó y fue bajo.
    if face_match_score is not None and face_match_score < 0.7:
        reasons.append("Face match score too low")

    # -------------------------
    # 6) Resultado final
    # -------------------------
    if len(reasons) == 0:
        status = "APPROVED"
        reject_reason = None
    else:
        status = "REJECTED"
        reject_reason = "; ".join(reasons)

    # Actualizar sesión
    session.status = status
    session.rejectReason = reject_reason
    update_session(session)

    return DecisionResult(
        sessionId=session_id,
        status=status,
        reason=reject_reason,
        documentValid=document_valid,
        documentValidationReason=document_validation_reason,
        ocrConfidence=ocr_conf,
        captureQuality=capture_quality,
        livenessScore=liveness_score,
        faceMatchScore=face_match_score,  # 👈 importante
    )