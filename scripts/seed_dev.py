#!/usr/bin/env python3
"""
Seed dev user and API key for local development.
Run: python scripts/seed_dev.py
Output: API key to use in X-API-Key header.
"""
import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.auth import hash_api_key
from api.db import Base, async_session_maker, engine
from api.models import APIKey, User


async def main():
    async with async_session_maker() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Check if dev user exists
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.email == "dev@localhost"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(email="dev@localhost")
            session.add(user)
            await session.flush()
            await session.refresh(user)
            print(f"Created user: {user.id}")

        # Create API key (plain key shown once)
        plain_key = "dev-api-key-" + user.id[:8]
        key_hash = hash_api_key(plain_key)
        result = await session.execute(select(APIKey).where(APIKey.key_hash == key_hash))
        if result.scalar_one_or_none():
            print("API key already exists. Use: X-API-Key: dev-api-key-...")
        else:
            api_key = APIKey(user_id=user.id, key_hash=key_hash, name="dev")
            session.add(api_key)
            await session.commit()
            print(f"\nDev API Key (use in X-API-Key header):\n  {plain_key}\n")


if __name__ == "__main__":
    asyncio.run(main())
