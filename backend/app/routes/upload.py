from fastapi import APIRouter, HTTPException, UploadFile
import shutil
import os

from app.services.pdf_loader import load_pdf
from app.services.chunker import chunk_text
from app.services.embeddings import get_embeddings
from app.services.vector_store import store_embeddings

router = APIRouter()
MAX_CHUNKS = 80

@router.post("/upload")
async def upload_pdf(file: UploadFile):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        return {"message": "Please upload a .pdf file"}

    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = load_pdf(file_path)
    chunks = chunk_text(text, chunk_size=1200, overlap=150)
    chunks = [c.strip() for c in chunks if c.strip()]
    if len(chunks) > MAX_CHUNKS:
        chunks = chunks[:MAX_CHUNKS]

    if not text.strip():
        os.remove(file_path)
        return {"message": "No extractable text found in the PDF"}

    try:
        embeddings = get_embeddings(chunks)
        stored = store_embeddings(embeddings, chunks)
        if stored == 0:
            raise ValueError("No vectors were stored in pgvector.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return {"message": "PDF processed successfully", "chunks": len(chunks), "stored": stored}
