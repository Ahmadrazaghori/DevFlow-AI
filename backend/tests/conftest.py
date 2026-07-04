"""Shared pytest fixtures.

Fixtures for a real test database and an httpx AsyncClient wired to the
FastAPI app are added in Phase 3 (Auth Module) once models exist. For
now this only wires basic pytest-asyncio + env loading so the test
suite is runnable from Step 1 onward.
"""

import os

os.environ.setdefault("APP_ENV", "development")
