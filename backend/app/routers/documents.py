"""documents.py -- upload, list, and clear the shared knowledge base."""
import io

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.config import MAX_UPLOAD_MB, RATE_LIMIT_UPLOAD, RATE_LIMIT_RESET
from app.document_processor import (
    DocumentProcessingError,
    SUPPORTED_EXTENSIONS,
    process_document,
)
from app.embeddings import embed_texts
from app.ratelimit import limiter
from app.schemas import DocumentsListResponse, UploadFileResult, UploadResponse
from app.vector_store import get_store

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.get("", response_model=DocumentsListResponse)
def list_documents():
    store = get_store()
    return DocumentsListResponse(documents=store.list_documents(), chunk_count=store.count())


@router.post("/upload", response_model=UploadResponse)
@limiter.limit(RATE_LIMIT_UPLOAD)
async def upload_documents(request: Request, files: list[UploadFile] = File(...)):
    store = get_store()
    already_indexed = set(store.list_documents())
    results: list[UploadFileResult] = []

    for f in files:
        ext = "." + f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
        if ext not in SUPPORTED_EXTENSIONS:
            results.append(UploadFileResult(
                filename=f.filename, status="error",
                detail=f"Unsupported file type '{ext}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}.",
            ))
            continue

        if f.filename in already_indexed:
            results.append(UploadFileResult(
                filename=f.filename, status="skipped", detail="Already in the knowledge base.",
            ))
            continue

        raw = await f.read()
        size_mb = len(raw) / (1024 * 1024)
        if size_mb > MAX_UPLOAD_MB:
            results.append(UploadFileResult(
                filename=f.filename, status="error",
                detail=f"{size_mb:.1f} MB exceeds the {MAX_UPLOAD_MB} MB limit.",
            ))
            continue

        try:
            chunks = process_document(io.BytesIO(raw), f.filename)
            embeddings = embed_texts([c.text for c in chunks])
            store.add_chunks(chunks, embeddings)
            already_indexed.add(f.filename)
            results.append(UploadFileResult(
                filename=f.filename, status="ok",
                detail=f"{len(chunks)} chunks indexed.", chunks_indexed=len(chunks),
            ))
        except DocumentProcessingError as e:
            results.append(UploadFileResult(filename=f.filename, status="error", detail=str(e)))
        except Exception as e:  # noqa: BLE001 - surface as a clean per-file error
            results.append(UploadFileResult(
                filename=f.filename, status="error", detail=f"Unexpected error: {e}",
            ))

    return UploadResponse(
        results=results, documents=store.list_documents(), chunk_count=store.count(),
    )


@router.delete("", response_model=DocumentsListResponse)
@limiter.limit(RATE_LIMIT_RESET)
def clear_documents(request: Request):
    store = get_store()
    store.reset()
    return DocumentsListResponse(documents=store.list_documents(), chunk_count=store.count())
