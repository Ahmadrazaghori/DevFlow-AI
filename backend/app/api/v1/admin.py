"""Admin-only endpoints.

Gated entirely by the require_superuser dependency. Organization- and
project-scoped role checks (Manager/Developer/Viewer) are added in the
Projects module (Phase 4), since those roles only make sense within a
specific project's context.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import require_superuser
from app.infrastructure.database.models.user import User
from app.infrastructure.database.session import get_db_session
from app.schemas.user import UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_superuser)])


@router.get("/users", response_model=list[UserResponse], summary="List all users (superuser only)")
async def list_users(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[UserResponse]:
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [UserResponse.model_validate(user) for user in users]
