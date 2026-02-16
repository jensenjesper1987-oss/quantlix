"""API key and password authentication."""
import hashlib
from typing import Annotated

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.models import APIKey, User


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_api_key(key: str) -> str:
    """Hash API key for storage (never store plain)."""
    return hashlib.sha256(key.encode()).hexdigest()


async def get_user_from_api_key(
    api_key: Annotated[str | None, Depends(api_key_header)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Resolve API key to user. Raises 401 if invalid or missing."""
    if not api_key or not api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header.",
        )
    key_hash = hash_api_key(api_key.strip())
    result = await db.execute(
        select(APIKey).where(APIKey.key_hash == key_hash)
    )
    api_key_row = result.scalar_one_or_none()
    if not api_key_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
    result = await db.execute(select(User).where(User.id == api_key_row.user_id))
    user = result.scalar_one()
    return user


async def get_current_api_key(
    api_key: Annotated[str | None, Depends(api_key_header)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> APIKey:
    """Resolve API key header to APIKey row. Raises 401 if invalid. For rotate/revoke flows."""
    if not api_key or not api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header.",
        )
    key_hash = hash_api_key(api_key.strip())
    result = await db.execute(select(APIKey).where(APIKey.key_hash == key_hash))
    api_key_row = result.scalar_one_or_none()
    if not api_key_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
    return api_key_row


# Type aliases for route dependencies
CurrentUser = Annotated[User, Depends(get_user_from_api_key)]
CurrentAPIKey = Annotated[APIKey, Depends(get_current_api_key)]
