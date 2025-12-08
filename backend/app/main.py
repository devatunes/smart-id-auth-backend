from fastapi import FastAPI

app = FastAPI(title="Smart Identity Auth API")


@app.get("/health")
def health():
    return {"status": "ok"}