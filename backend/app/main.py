"""
main.py -- FastAPI entrypoint.

Wires together CORS, the document/chat/test routers, per-IP rate limiting,
a health check for Render, and a global exception handler so the frontend
always gets clean JSON instead of a raw 500 stack trace.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import ALLOWED_ORIGINS, ENVIRONMENT
from app.ratelimit import limiter
from app.routers import chat, documents, test

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-doc-assistant")

app = FastAPI(
    title="AI Document Knowledge Assistant API",
    description="RAG over your own PDF/Word/PowerPoint documents, with local embeddings and Groq for generation.",
    version="1.0.0",
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": f"Too many requests — please slow down ({exc.detail})."},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our end. Please try again shortly."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)


@app.get("/health", tags=["Health"])
def health_check():
    """Used by the Docker HEALTHCHECK and Render health checks."""
    return {"status": "ok", "environment": ENVIRONMENT}


app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(test.router)
