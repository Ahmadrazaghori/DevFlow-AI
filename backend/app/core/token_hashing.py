"""Hashing helper for tokens we need to look up later (refresh tokens).

Separate from password hashing: Argon2 is deliberately slow (that's
the point for passwords). Refresh token lookups happen on every
API request that needs a new access token, so we use a fast
deterministic hash (SHA-256) instead — security here comes from the
token's own entropy (256-bit random JWT), not from hashing cost.
"""

import hashlib


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
