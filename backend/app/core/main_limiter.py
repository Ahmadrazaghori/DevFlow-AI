"""Shared slowapi rate limiter instance.

Lives in its own module (not app.main) so route files can import and
apply @limiter.limit(...) decorators without creating a circular
import with the app factory in main.py.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])
