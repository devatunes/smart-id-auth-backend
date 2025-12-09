from fastapi import UploadFile

from app.models.schemas import LivenessResult
from app.services.session_service import update_session
from app.helpers.session_helper import ensure_session
from app.helpers.image_helper import ensure_image_file
from app.services.liveness_service import analyze_liveness
from app.services.face_service import (
    extract_face_descriptor,
    compute_face_similarity,
)


async def process_selfie_for_session(session_id: str, file: UploadFile) -> LivenessResult:
    """
    Orquesta el flujo de selfie para una sesión:
      1. Valida sesión.
      2. Valida que el archivo sea una imagen.
      3. Ejecuta liveness.
      4. Extrae descriptor de rostro de la selfie.
      5. Si existe descriptor de documento, calcula faceMatchScore.
      6. Actualiza la sesión.
    """

    # 1) Validar sesión
    session = ensure_session(session_id)

    # 2) Validar archivo
    ensure_image_file(file)

    # 3) Ejecutar liveness
    liveness_result: LivenessResult = await analyze_liveness(file)

    session.selfieProcessed = True
    session.livenessScore = liveness_result.score
    session.livenessReason = liveness_result.reason

    # 4) Extraer descriptor de la selfie y calcular face match
    try:
        # Volver a inicio del archivo porque analyze_liveness ya leyó el stream
        file.file.seek(0)
        image_bytes = await file.read()
        selfie_desc = extract_face_descriptor(image_bytes)
        session.selfieFaceDescriptor = selfie_desc

        # 5) Si tenemos rostro de documento y de selfie → faceMatchScore
        if selfie_desc is not None and getattr(session, "documentFaceDescriptor", None):
            face_score = compute_face_similarity(
                session.documentFaceDescriptor,
                selfie_desc,
            )
            session.faceMatchScore = face_score
        else:
            session.faceMatchScore = None
    except Exception:
        # Si algo falla, no rompemos el flujo, solo dejamos sin face match
        session.selfieFaceDescriptor = None
        session.faceMatchScore = None

    # 6) Guardar cambios de sesión
    update_session(session)

    return liveness_result