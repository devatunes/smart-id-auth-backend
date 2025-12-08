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
    
class DocumentOcrResult(BaseModel):
    """
    Resultado del OCR sobre el documento de identidad.
    Esto es lo que más adelante llenará EasyOCR/Tesseract.
    """
    documentNumber: str
    fullName: str
    expiryDate: Optional[str] = None
    ocrConfidence: float
    captureQuality: Literal["GOOD", "BLURRY", "PARTIAL", "OUT_OF_FRAME"]