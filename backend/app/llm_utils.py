"""
llm_utils.py
------------
Client-side protection for the one place this app calls an external LLM
API (Groq, in rag_pipeline.py):

1. A sliding-window rate limiter that throttles outgoing requests to stay
   under a per-minute budget, instead of firing as fast as users click and
   hoping Groq doesn't 429 us. This matters more once the app is a public
   demo link than it did running locally for one person.
2. Retry with exponential backoff + jitter for the rare 429/5xx/timeout,
   so a single blip doesn't surface as an error to the user.
"""
import logging
import os
import threading
import time
from collections import deque
from functools import wraps

from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

logger = logging.getLogger("ai-doc-assistant.llm")

GROQ_MAX_REQUESTS_PER_MINUTE = int(os.getenv("GROQ_MAX_REQUESTS_PER_MINUTE", "25"))
GROQ_MAX_RETRIES = int(os.getenv("GROQ_MAX_RETRIES", "4"))


class SlidingWindowRateLimiter:
    """Blocks the caller (sleeping) until sending another request would
    stay within `max_per_minute` requests in the trailing 60 seconds."""

    def __init__(self, max_per_minute: int):
        self.max_per_minute = max(1, max_per_minute)
        self._timestamps: deque[float] = deque()
        self._lock = threading.Lock()

    def acquire(self):
        with self._lock:
            now = time.monotonic()
            window_start = now - 60
            while self._timestamps and self._timestamps[0] < window_start:
                self._timestamps.popleft()

            sleep_for = 0
            if len(self._timestamps) >= self.max_per_minute:
                sleep_for = 60 - (now - self._timestamps[0]) + 0.05
                logger.info(
                    "Groq rate limiter: at %d/%d requests this minute, sleeping %.1fs",
                    len(self._timestamps), self.max_per_minute, sleep_for,
                )

        if sleep_for > 0:
            time.sleep(sleep_for)

        with self._lock:
            self._timestamps.append(time.monotonic())


_rate_limiter = SlidingWindowRateLimiter(GROQ_MAX_REQUESTS_PER_MINUTE)


def _is_retryable(exc: BaseException) -> bool:
    status = getattr(exc, "status_code", None) or getattr(
        getattr(exc, "response", None), "status_code", None
    )
    if status in (429, 500, 502, 503, 504):
        return True
    name = exc.__class__.__name__.lower()
    return "ratelimit" in name or "timeout" in name or "apiconnection" in name


def with_groq_protection(fn):
    """Decorator: rate-limit + retry-with-backoff any callable that issues
    a Groq API call."""

    @retry(
        retry=retry_if_exception(_is_retryable),
        wait=wait_exponential_jitter(initial=1, max=20),
        stop=stop_after_attempt(GROQ_MAX_RETRIES),
        reraise=True,
    )
    @wraps(fn)
    def wrapper(*args, **kwargs):
        _rate_limiter.acquire()
        return fn(*args, **kwargs)

    return wrapper
