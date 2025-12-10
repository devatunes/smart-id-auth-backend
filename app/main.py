from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pathlib import Path
import json

from app.routes.auth import router as auth_router

# --------------------------------------------------
# App base
# --------------------------------------------------
app = FastAPI(
    title="Smart Identity Auth API",
    version="0.1.0",
    description="Kata de autenticación con OCR, liveness y face match usando FastAPI.",
)

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# Generar OpenAPI al arrancar el servidor
# --------------------------------------------------
@app.on_event("startup")
async def generate_openapi_file() -> None:
    """
    En cada arranque del servidor genera docs/openapi.json
    a partir del esquema real de la app.
    """
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    output_file = docs_dir / "openapi.json"
    output_file.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[startup] OpenAPI schema actualizado en: {output_file}")