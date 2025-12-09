from datetime import datetime
from typing import Dict, Optional

from app.models.schemas import AuthSession

_sessions: Dict[str, AuthSession] = {}


def create_session(session_id: str) -> AuthSession:
    session = AuthSession(
        sessionId=session_id,
        createdAt=datetime.utcnow(),
    )
    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> Optional[AuthSession]:
    return _sessions.get(session_id)


def get_all_sessions() -> Dict[str, AuthSession]:
    return _sessions


def update_session(session: AuthSession) -> AuthSession:
    _sessions[session.sessionId] = session
    return session