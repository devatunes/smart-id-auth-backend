from fastapi import APIRouter, UploadFile, File, HTTPException, status
import uuid

from app.models.schemas import (
    StartAuthResponse,
    DocumentOcrResult,
    DocumentValidationResult,
    LivenessResult,
    DecisionResult,
)
from app.services.session_service import create_session, get_session
from app.services.ocr_service import analyze_document_ocr
from app.services.document_repository import get_document
from app.services.liveness_service import analyze_liveness

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/start", response_model=StartAuthResponse)
def start_authentication():
    session_id = str(uuid.uuid4())

    # Crear y registrar la sesión en memoria
    session = create_session(session_id=session_id)

    return StartAuthResponse(
        sessionId=session.sessionId,
        message="Authentication session started",
        createdAt=session.createdAt,
    )
    
@router.get("/session-debug")
def session_debug(sessionId: str):
    session = get_session(sessionId)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/document")
async def upload_document(
    sessionId: str,
    file: UploadFile = File(...),
):
    """
    Recibe la imagen del documento asociada a una sesión,
    ejecuta OCR (por ahora mock) y valida el documento contra el repositorio local.
    """

    # 1. Validar que la sesión exista
    session = get_session(sessionId)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # 2. Validar tipo de archivo básico
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only image files are allowed.",
        )

    # 3. Ejecutar OCR (mock por ahora)
    ocr_result: DocumentOcrResult = await analyze_document_ocr(file)

    # 4. Validar documento contra el repositorio local
    record = get_document(ocr_result.documentNumber)

    if record is None:
        validation = DocumentValidationResult(
            isValid=False,
            reason="Document not found in local repository",
        )
    else:
        # Aquí podríamos validar expiración, estado, etc.
        if record.isActive:
            validation = DocumentValidationResult(
                isValid=True,
                reason=None,
            )
        else:
            validation = DocumentValidationResult(
                isValid=False,
                reason="Document is inactive",
            )

    # 5. Marcar en la sesión que ya se procesó el documento
    session.documentProcessed = True
    # Más adelante podemos guardar isValid/reason dentro de la sesión también.

    return {
        "sessionId": session.sessionId,
        "filename": file.filename,
        "contentType": file.content_type,
        "message": "Document received and processed (OCR + validation stub)",
        "ocrResult": ocr_result,
        "validation": validation,
    }
    
@router.post("/selfie")
async def upload_selfie(
    sessionId: str,
    file: UploadFile = File(...),
):
    """
    Recibe la selfie asociada a una sesión de autenticación
    y ejecuta un análisis de liveness (por ahora stub).
    """

    # 1. Validar que la sesión exista
    session = get_session(sessionId)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # 2. Validar tipo de archivo básico
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only image files are allowed.",
        )

    # 3. Ejecutar liveness (stub)
    liveness_result: LivenessResult = await analyze_liveness(file)

    # 4. Actualizar sesión
    session.selfieProcessed = True
    session.livenessScore = liveness_result.score

    # 5. (Más adelante) Aquí conectaremos:
    #    - face match con el rostro del documento
    #    - decisiones de aprobación/rechazo usando livenessScore, OCR, etc.

    return {
        "sessionId": session.sessionId,
        "filename": file.filename,
        "contentType": file.content_type,
        "message": "Selfie received and liveness analyzed (stub)",
        "liveness": liveness_result,
    }
    
@router.post("/decision", response_model=DecisionResult)
def finalize_decision(sessionId: str):
    """
    Toma la decisión final de autenticación basada en:
    - Validación del documento
    - Liveness score
    - Estado de la sesión
    """

    session = get_session(sessionId)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 1. Validar que el documento y selfie hayan sido recibidos
    if not session.documentProcessed:
        session.status = "REJECTED"
        session.rejectReason = "Document not processed"
        return DecisionResult(
            sessionId=sessionId,
            status="REJECTED",
            reason=session.rejectReason,
            livenessScore=session.livenessScore,
            documentValid=False,
        )

    if not session.selfieProcessed:
        session.status = "REJECTED"
        session.rejectReason = "Selfie not processed"
        return DecisionResult(
            sessionId=sessionId,
            status="REJECTED",
            reason=session.rejectReason,
            livenessScore=session.livenessScore,
            documentValid=True,  # documento sí recibido
        )

    # 2. Validar OCR + documento (mock por ahora)
    # Por ahora contamos como válido cualquier documento no rechazado previamente
    document_valid = True  # en pasos posteriores esto vendrá de la validación real

    # 3. Validar liveness
    if session.livenessScore is None or session.livenessScore < 0.8:
        session.status = "REJECTED"
        session.rejectReason = "Liveness score too low"
        return DecisionResult(
            sessionId=sessionId,
            status="REJECTED",
            reason=session.rejectReason,
            livenessScore=session.livenessScore,
            documentValid=document_valid,
        )

    # 4. Si todo está OK → aprobación
    session.status = "APPROVED"
    session.rejectReason = None

    return DecisionResult(
        sessionId=sessionId,
        status="APPROVED",
        reason=None,
        livenessScore=session.livenessScore,
        documentValid=document_valid,
    )