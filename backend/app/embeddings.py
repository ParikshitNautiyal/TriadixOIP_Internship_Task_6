"""
embeddings.py
-------------
Handles the "text embeddings" hands-on concept.

Uses fastembed (ONNX Runtime under the hood) to run a local embedding
model, so embedding generation is free and doesn't require network calls
(aligned with the project's goal of avoiding unnecessary API usage) --
without pulling in PyTorch/transformers the way sentence-transformers
does. Same underlying MiniLM model, a much smaller dependency footprint
and no C++ build step. The model is loaded once and cached.
"""

from functools import lru_cache
from typing import List

from fastembed import TextEmbedding

from app.config import EMBEDDING_MODEL_NAME


@lru_cache(maxsize=1)
def get_embedding_model() -> TextEmbedding:
    """
    Load (and cache) the local embedding model.

    lru_cache ensures the model is only loaded into memory once per
    process, even though Streamlit re-runs the script on every interaction.
    """
    return TextEmbedding(model_name=EMBEDDING_MODEL_NAME)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a batch of text strings. Returns a list of float vectors."""
    if not texts:
        return []
    model = get_embedding_model()
    # model.embed() returns a generator of numpy arrays, one per input text.
    return [vec.tolist() for vec in model.embed(list(texts))]


def embed_query(query: str) -> List[float]:
    """Embed a single query string (e.g. the user's question)."""
    model = get_embedding_model()
    return next(model.embed([query])).tolist()
