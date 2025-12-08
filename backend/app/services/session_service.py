from datetime import datetime
from typing import Dict, Optional

from app.models.schemas import AuthSession


# Almacén de sesiones en memoria
_sessions: Dict[str, AuthSession] = {}


def create_session(session_id: str) -> AuthSession:
    """
    Crea una nueva sesión de autenticación y la guarda en memoria.
    """
    session = AuthSession(
        sessionId=session_id,
        createdAt=datetime.utcnow(),
    )
    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> Optional[AuthSession]:
    """
    Obtiene una sesión por su ID, si existe.
    """
    return _sessions.get(session_id)


def get_all_sessions() -> Dict[str, AuthSession]:
    """
    Devuelve todas las sesiones (útil para métricas más adelante).
    """
    return _sessions