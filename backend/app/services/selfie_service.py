from fastapi import UploadFile
from app.models.schemas import LivenessResult
from app.services.session_service import update_session
from app.helpers.session_helper import ensure_session
from app.helpers.image_helper import ensure_image_file
from app.services.liveness_service import analyze_liveness


async def process_selfie_for_session(session_id: str, file: UploadFile) -> LivenessResult:

    # 1) Validar sesión
    session = ensure_session(session_id)

    # 2) Validar archivo
    ensure_image_file(file)

    # 3) Ejecutar liveness
    liveness_result: LivenessResult = await analyze_liveness(file)

    # 4) Actualizar sesión
    session.selfieProcessed = True
    session.livenessScore = liveness_result.score
    update_session(session)

    return liveness_result