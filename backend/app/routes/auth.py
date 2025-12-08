from fastapi import APIRouter
import uuid

from app.models.schemas import StartAuthResponse
from app.services.session_service import create_session

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