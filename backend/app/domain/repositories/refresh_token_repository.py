"""Abstract RefreshToken repository contract."""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from app.infrastructure.database.models.auth import RefreshToken


class RefreshTokenRepository(ABC):
    @abstractmethod
    async def create(
        self, *, user_id: uuid.UUID, token_hash: str, expires_at: datetime, device_info: str | None
    ) -> RefreshToken: ...

    @abstractmethod
    async def get_by_hash(self, token_hash: str) -> RefreshToken | None: ...

    @abstractmethod
    async def revoke(self, token: RefreshToken) -> None: ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None: ...
