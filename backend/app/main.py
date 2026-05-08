from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routes import upload, chat


def _allowed_origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS", "")
    if configured.strip():
        return [origin.strip() for origin in configured.split(",") if origin.strip()]

    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    defaults = ["http://localhost:3000", "http://127.0.0.1:3000"]
    if frontend_url:
        defaults.insert(0, frontend_url)
    return defaults


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/")
def root():
    return {"status": "running"}
