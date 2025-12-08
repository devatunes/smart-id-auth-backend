from fastapi import APIRouter, UploadFile, File, HTTPException, status
import uuid

from app.models.schemas import StartAuthResponse
from app.services.session_service import create_session, get_session

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
    Recibe la imagen del documento asociada a una sesión.
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

    # 3. Marcar en la sesión que ya se procesó el documento
    session.documentProcessed = True

    # 4. (Más adelante) acá guardaremos el archivo en disco/tmp
    #    y llamaremos al servicio OCR.

    return {
        "sessionId": session.sessionId,
        "filename": file.filename,
        "contentType": file.content_type,
        "message": "Document received successfully",
    }