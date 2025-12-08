from fastapi import APIRouter, UploadFile, File, HTTPException, status
import uuid

from app.models.schemas import (
    StartAuthResponse,
    DocumentOcrResult,
    DocumentValidationResult,
)
from app.services.session_service import create_session, get_session
from app.services.ocr_service import analyze_document_ocr
from app.services.document_repository import get_document

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
