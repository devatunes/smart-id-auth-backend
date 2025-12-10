# app/routes/auth.py

from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid

from app.models.schemas import (
    StartAuthResponse,
    DecisionResult,
    AuthMetrics,
)

from app.services.session_service import (
    create_session,
    get_session,
)
from app.services.document_service import process_document_for_session
from app.services.selfie_service import process_selfie_for_session
from app.services.decision_service import evaluate_authentication
# from app.services.metrics_service import compute_auth_metrics
from app.helpers.image_helper import InvalidImageError
from app.helpers.session_helper import SessionNotFoundError

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])


@router.post("/session", response_model=StartAuthResponse)
def start_authentication():
    """
    Crea una nueva sesión de autenticación y la devuelve al cliente.
    """
    session_id = str(uuid.uuid4())

    # Crear y registrar la sesión en memoria
    session = create_session(session_id=session_id)

    return StartAuthResponse(
        sessionId=session.sessionId,
        message="Authentication session started",
        createdAt=session.createdAt,
    )

@router.post("/document")
async def upload_document(
    sessionId: str,
    file: UploadFile = File(...),
):
    """
    Recibe la imagen del documento asociada a una sesión
    y delega el flujo completo al document_service:
      - validación de sesión
      - validación de imagen
      - OCR
      - validación contra repositorio local
      - actualización de sesión
    """

    try:
        result = await process_document_for_session(sessionId, file)
    except InvalidImageError as e:
        # Archivo no es una imagen válida
        raise HTTPException(status_code=400, detail=str(e))
    except SessionNotFoundError:
        # La sesión no existe
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "sessionId": sessionId,
        "filename": file.filename,
        "contentType": file.content_type,
        "message": "Document received and processed (OCR + validation)",
        "ocrResult": result.ocrResult,
        "validation": result.validation,
    }


@router.post("/selfie")
async def upload_selfie(
    sessionId: str,
    file: UploadFile = File(...),
):
    """
    Recibe la selfie asociada a una sesión de autenticación
    y delega el flujo al selfie_service:
      - validación de sesión
      - validación de imagen
      - análisis de liveness
      - actualización de sesión
    """

    try:
        liveness_result = await process_selfie_for_session(sessionId, file)
    except InvalidImageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "sessionId": sessionId,
        "filename": file.filename,
        "contentType": file.content_type,
        "message": "Selfie received and liveness analyzed (heuristic CV model)",
        "liveness": liveness_result,
    }


@router.post("/decision", response_model=DecisionResult)
def finalize_decision(sessionId: str):
    """
    Toma la decisión final de autenticación usando el decision_service:
      - revisa flags de flujo (document/selfie procesados)
      - valida documento, OCR y liveness
      - actualiza el estado de la sesión (APPROVED / REJECTED)
      - devuelve un DecisionResult con todos los detalles
    """
    try:
        return evaluate_authentication(sessionId)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")


# @router.get("/session-debug")
# def session_debug(sessionId: str):
#     """
#     Endpoint de apoyo para ver el estado crudo de una sesión.
#     (solo para debugging / demo).
#     """
#     session = get_session(sessionId)
#     if not session:
#         raise HTTPException(status_code=404, detail="Session not found")
#     return session


# @router.get("/metrics", response_model=AuthMetrics)
# def get_auth_metrics():
#     """
#     Devuelve métricas globales de autenticación usando metrics_service:
#       - total de sesiones
#       - aprobadas / rechazadas
#       - tasas %
#       - razones de rechazo agrupadas
#     """
#     return compute_auth_metrics()