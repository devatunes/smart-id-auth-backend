from app.services.session_service import get_session


class SessionNotFoundError(ValueError):
    pass


def ensure_session(session_id: str):
    session = get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session {session_id} not found")
    return session