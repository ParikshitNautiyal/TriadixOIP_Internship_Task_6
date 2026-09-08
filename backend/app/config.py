"""
config.py
---------
Central configuration for the AI Document Knowledge Assistant API.

Loads settings from environment variables (via a .env file locally, or
platform env vars on Render) and exposes them as simple constants that the
rest of the app imports from.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# LLM (Groq) settings
# ---------------------------------------------------------------------------
# Groq is used only for the final answer-generation step. Retrieval and
# embeddings are fully local, so the LLM is the only paid/networked call.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

# ---------------------------------------------------------------------------
# Embedding model (local, via sentence-transformers)
# ---------------------------------------------------------------------------
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

# ---------------------------------------------------------------------------
# Chunking settings
# ---------------------------------------------------------------------------
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# ---------------------------------------------------------------------------
# Vector store (ChromaDB) settings
# ---------------------------------------------------------------------------
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "/app/data/chroma_store")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "pdf_knowledge_base")

# ---------------------------------------------------------------------------
# Retrieval settings
# ---------------------------------------------------------------------------
TOP_K = int(os.getenv("TOP_K", "4"))
MAX_RELEVANT_DISTANCE = float(os.getenv("MAX_RELEVANT_DISTANCE", "0.9"))

# ---------------------------------------------------------------------------
# Uploads
# ---------------------------------------------------------------------------
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))

# ---------------------------------------------------------------------------
# App / CORS / networking
# ---------------------------------------------------------------------------
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
# Comma-separated list of allowed frontend origins, e.g.
# "https://your-app.vercel.app,http://localhost:5173"
ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()
]

# ---------------------------------------------------------------------------
# Rate limiting (protects the public demo + the Groq free-tier quota)
# ---------------------------------------------------------------------------
RATE_LIMIT_CHAT = os.getenv("RATE_LIMIT_CHAT", "15/minute")
RATE_LIMIT_UPLOAD = os.getenv("RATE_LIMIT_UPLOAD", "10/minute")
RATE_LIMIT_TEST = os.getenv("RATE_LIMIT_TEST", "5/minute")
RATE_LIMIT_RESET = os.getenv("RATE_LIMIT_RESET", "5/minute")
