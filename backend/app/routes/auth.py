from fastapi import APIRouter
import uuid
from datetime import datetime

from app.models.schemas import StartAuthResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/start", response_model=StartAuthResponse)
def start_authentication():
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()

    return StartAuthResponse(
        sessionId=session_id,
        message="Authentication session started",
        createdAt=now,
    )