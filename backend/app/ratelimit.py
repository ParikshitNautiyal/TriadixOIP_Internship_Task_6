"""Per-client-IP request throttling for the public demo — protects both
server resources and the shared Groq free-tier quota from being hammered
by one visitor."""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
