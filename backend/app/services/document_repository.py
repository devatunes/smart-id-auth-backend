from typing import Dict, Optional
from pydantic import BaseModel


class DocumentRecord(BaseModel):
    documentNumber: str
    fullName: str
    expiryDate: Optional[str] = None  # ISO string "YYYY-MM-DD"
    isActive: bool = True


# Mock de documentos válidos en el sistema
# En un caso real esto sería una BD o servicio externo.
_DOCUMENTS: Dict[str, DocumentRecord] = {
    "123456789": DocumentRecord(
        documentNumber="123456789",
        fullName="NOMBRE APELLIDO MOCK",
        expiryDate="2030-12-31",
        isActive=True,
    ),
    "987654321": DocumentRecord(
        documentNumber="987654321",
        fullName="OTRO NOMBRE MOCK",
        expiryDate="2028-05-10",
        isActive=True,
    ),
    # Puedes agregar más registros para pruebas.
}


def get_document(document_number: str) -> Optional[DocumentRecord]:
    """
    Busca un documento por número en el repositorio local.
    """
    return _DOCUMENTS.get(document_number)