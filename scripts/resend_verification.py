#!/usr/bin/env python3
"""
Resend verification email to the last N registered users (unverified only).

Usage:
  python scripts/resend_verification.py [N]
  kubectl exec deploy/api -n quantlix -- python scripts/resend_verification.py 2

Defaults to last 2 users if N not specified.
"""
import asyncio
import os
import secrets
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from api.db import async_session_maker
from api.email import send_verification_email
from api.models import User


async def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2

    async with async_session_maker() as session:
        result = await session.execute(
            select(User)
            .where(User.email_verified == False)
            .order_by(User.created_at.desc())
            .limit(n)
        )
        users = result.scalars().all()

        if not users:
            print("No unverified users found.")
            return

        print(f"Resending verification to {len(users)} user(s):")
        for user in users:
            token = secrets.token_urlsafe(32)
            user.email_verification_token = token
            await session.flush()
            try:
                await send_verification_email(user.email, token)
                print(f"  ✓ {user.email}")
            except Exception as e:
                print(f"  ✗ {user.email}: {e}")

        await session.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
