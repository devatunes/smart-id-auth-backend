from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal


class StartAuthResponse(BaseModel):
    sessionId: str
    message: str
    createdAt: datetime


class AuthSession(BaseModel):
    """
    Representa el estado de una sesión de autenticación.
    Este modelo se usará para trazabilidad y métricas.
    """
    sessionId: str
    createdAt: datetime
    status: Literal["PENDING", "APPROVED", "REJECTED"] = "PENDING"
    documentProcessed: bool = False
    selfieProcessed: bool = False
    livenessScore: Optional[float] = None
    faceMatchScore: Optional[float] = None
    rejectReason: Optional[str] = None