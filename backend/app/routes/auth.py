from fastapi import APIRouter
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/start")
def start_authentication():
    session_id = str(uuid.uuid4())
    return {
        "sessionId": session_id,
        "message": "Authentication session started"
    }