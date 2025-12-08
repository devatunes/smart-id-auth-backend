from fastapi import UploadFile
from app.models.schemas import DocumentOcrResult


async def analyze_document_ocr(file: UploadFile) -> DocumentOcrResult:
    """
    Analiza la imagen del documento.
    Por ahora es un STUB: devuelve datos mock.
    Más adelante aquí integraremos EasyOCR/Tesseract.
    """

    # TODO: Leer bytes del archivo, preprocesar imagen y aplicar OCR real.
    # image_bytes = await file.read()
    # ... OCR real ...

    # Por ahora devolvemos un resultado simulado.
    return DocumentOcrResult(
        documentNumber="123456789",
        fullName="NOMBRE APELLIDO MOCK",
        expiryDate="2030-12-31",
        ocrConfidence=0.95,
        captureQuality="GOOD",
    )