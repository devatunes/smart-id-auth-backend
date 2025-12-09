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
    Usada para trazabilidad y decisiones.
    """

    sessionId: str
    createdAt: datetime

    # Estado general
    status: Literal["PENDING", "APPROVED", "REJECTED"] = "PENDING"
    rejectReason: Optional[str] = None

    # ---- Documento ----
    documentProcessed: bool = False
    documentValid: Optional[bool] = None
    documentValidationReason: Optional[str] = None
    ocrConfidence: Optional[float] = None
    captureQuality: Optional[str] = None
    documentFaceDescriptor: Optional[list[float]] = None  # FaceNet 512D

    # ---- Selfie ----
    selfieProcessed: bool = False
    livenessScore: Optional[float] = None
    livenessReason: Optional[str] = None
    selfieFaceDescriptor: Optional[list[float]] = None

    # ---- Face match ----
    faceMatchScore: Optional[float] = None
    
class DocumentOcrResult(BaseModel):
    """
    Resultado del OCR sobre el documento de identidad.
    Esto es lo que más adelante llenará EasyOCR
    """
    documentNumber: str
    givenNames: Optional[str] = None   # NOMBRES
    surnames: Optional[str] = None     # APELLIDOS
    expiryDate: Optional[str] = None
    ocrConfidence: float
    captureQuality: Literal["GOOD", "BLURRY", "PARTIAL", "OUT_OF_FRAME"]
    
class DocumentValidationResult(BaseModel):
    isValid: bool
    reason: Optional[str] = None
    
class LivenessResult(BaseModel):
    score: float                 # 0.0 a 1.0
    isLive: bool                 # True si se considera persona real
    reason: Optional[str] = None # Texto corto explicando el resultado


class DecisionResult(BaseModel):
    sessionId: str
    status: Literal["APPROVED", "REJECTED"]
    reason: Optional[str] = None

    documentValid: Optional[bool] = None
    documentValidationReason: Optional[str] = None
    ocrConfidence: Optional[float] = None
    captureQuality: Optional[str] = None

    livenessScore: Optional[float] = None
    faceMatchScore: Optional[float] = None
    
class AuthMetrics(BaseModel):
    totalSessions: int
    approved: int
    rejected: int
    approvalRate: float
    rejectionRate: float
    rejectionReasons: dict[str, int]  # ejemplo: {"Liveness low": 4, "Document invalid": 2}