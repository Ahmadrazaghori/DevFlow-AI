"""Abstract User repository contract.

The domain and application layers depend on this interface, never on
the concrete SQLAlchemy implementation — that's what makes the
business logic testable without a real database (swap in a fake
implementation for unit tests) and keeps SQLAlchemy an infrastructure
detail rather than a pervasive dependency.
"""

import uuid
from abc import ABC, abstractmethod

from app.infrastructure.database.models.user import User


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def create(self, *, email: str, hashed_password: str, full_name: str) -> User: ...

    @abstractmethod
    async def update(self, user: User) -> User: ...
