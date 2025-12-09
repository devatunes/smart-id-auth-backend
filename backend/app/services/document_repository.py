from typing import Dict, Optional
from pydantic import BaseModel


class DocumentRecord(BaseModel):
    documentNumber: str
    givenNames: str
    surnames: str
    expiryDate: Optional[str] = None  # ISO string "YYYY-MM-DD"
    isActive: bool = True


# Mock de documentos válidos en el sistema
# En un caso real esto sería una BD o servicio externo.
_DOCUMENTS: Dict[str, DocumentRecord] = {
    "123456789": DocumentRecord(
        documentNumber="123456789",
        givenNames="NOMBRES",
        surnames="APELLIDOS",
        expiryDate="2030-12-31",
        isActive=True,
    ),
    "1082997388": DocumentRecord(
        documentNumber="1082997388",
        givenNames="ALVARO LUIS",
        surnames="RODRIGUEZ ATUNEZ",
        expiryDate="2025-06-30",
        isActive=True,
    ),
    # Puedes agregar más registros para pruebas.
}


def get_document(document_number: str) -> Optional[DocumentRecord]:
    """
    Busca un documento por número en el repositorio local.
    """
    return _DOCUMENTS.get(document_number)