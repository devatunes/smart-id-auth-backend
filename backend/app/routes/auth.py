from fastapi import APIRouter, UploadFile, File, HTTPException, status
import uuid

from app.models.schemas import StartAuthResponse, DocumentOcrResult
from app.services.session_service import create_session, get_session
from app.services.ocr_service import analyze_document_ocr

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


@router.post("/document")
async def upload_document(
    sessionId: str,
    file: UploadFile = File(...),
):
    """
    Recibe la imagen del documento asociada a una sesión,
    ejecuta OCR (por ahora mock) y marca la sesión como procesada.
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

    # 4. Marcar en la sesión que ya se procesó el documento
    session.documentProcessed = True
    # Más adelante podremos guardar en la sesión:
    # session.ocrConfidence = ocr_result.ocrConfidence
    # session.captureQuality = ocr_result.captureQuality
    # etc.

    return {
        "sessionId": session.sessionId,
        "filename": file.filename,
        "contentType": file.content_type,
        "message": "Document received and processed (OCR stub)",
        "ocrResult": ocr_result,
    }
    
@router.get("/session-debug")
def session_debug(sessionId: str):
    session = get_session(sessionId)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session