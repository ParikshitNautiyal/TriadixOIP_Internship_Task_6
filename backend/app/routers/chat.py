"""chat.py -- ask a question against the shared knowledge base."""
from fastapi import APIRouter, HTTPException, Request

from app.config import RATE_LIMIT_CHAT
from app.rag_pipeline import generate_answer
from app.ratelimit import limiter
from app.retrieval import retrieve_relevant_chunks
from app.schemas import ChatRequest, ChatResponse, SourceOut
from app.vector_store import get_store

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
@limiter.limit(RATE_LIMIT_CHAT)
def chat(request: Request, payload: ChatRequest):
    store = get_store()
    if store.count() == 0:
        raise HTTPException(400, "The knowledge base is empty — upload a document first.")

    try:
        chunks = retrieve_relevant_chunks(payload.question, store)
        result = generate_answer(payload.question, chunks)
    except RuntimeError as e:
        raise HTTPException(500, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Something went wrong generating the answer: {e}")

    return ChatResponse(
        answer=result.answer,
        sources=[SourceOut(**s) for s in result.sources],
        grounded=result.grounded,
    )
