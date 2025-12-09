from fastapi import UploadFile
from pydantic import BaseModel

from app.models.schemas import DocumentOcrResult, DocumentValidationResult
from app.services.ocr_service import analyze_document_ocr
from app.repositories.document_repository import get_document
from app.services.session_service import update_session
from app.helpers.session_helper import ensure_session
from app.helpers.image_helper import ensure_image_file
from app.services.face_service import extract_face_descriptor


class DocumentFlowResult(BaseModel):
    """
    Resultado agregado del flujo de documento:
    - OCR del documento
    - Validación contra el repositorio local
    """
    ocrResult: DocumentOcrResult
    validation: DocumentValidationResult


async def process_document_for_session(
    session_id: str,
    file: UploadFile,
) -> DocumentFlowResult:
    """
    Orquesta el flujo de procesamiento de documento para una sesión:
      1. Obtiene y valida la sesión (helper de sesión).
      2. Valida que el archivo sea una imagen (helper de imagen).
      3. Ejecuta OCR real sobre el documento.
      4. Valida el documento contra el repositorio local.
      5. Extrae descriptor de rostro del documento y actualiza sesión.
      6. Devuelve un objeto con OCR + resultado de validación.
    """
    
    # 1) Obtener sesión (lanza SessionNotFoundError si no existe)
    session = ensure_session(session_id)

    # 2) Validar que sea imagen (lanza InvalidImageError si no lo es)
    ensure_image_file(file)

    # 3) OCR real
    ocr_result: DocumentOcrResult = await analyze_document_ocr(file)

    # 4) Validación contra repositorio local
    record = get_document(ocr_result.documentNumber)

    if record is None:
        validation = DocumentValidationResult(
            isValid=False,
            reason="Document not found in local repository",
        )
    elif record.isActive:
        validation = DocumentValidationResult(
            isValid=True,
            reason=None,
        )
    else:
        validation = DocumentValidationResult(
            isValid=False,
            reason="Document is inactive",
        )

    # 5) Actualizar sesión con la info del documento y el OCR
    session.documentProcessed = True
    session.documentValid = validation.isValid
    session.documentValidationReason = validation.reason
    session.ocrConfidence = ocr_result.ocrConfidence
    session.captureQuality = ocr_result.captureQuality

    # 👇 NUEVO: extraer descriptor de rostro del documento para face match
    try:
        # Volver al inicio del archivo porque analyze_document_ocr ya leyó el stream
        file.file.seek(0)
        image_bytes = await file.read()
        doc_desc = extract_face_descriptor(image_bytes)
        session.documentFaceDescriptor = doc_desc
    except Exception:
        # Si algo falla, dejamos el descriptor en None y no rompemos el flujo
        session.documentFaceDescriptor = None

    update_session(session)

    # 6) Devolver resultado agregado del flujo
    return DocumentFlowResult(
        ocrResult=ocr_result,
        validation=validation,
    )