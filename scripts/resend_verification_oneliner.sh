#!/bin/bash
# Resend verification to last 2 unverified users - runs inline in API pod (no rebuild needed)
kubectl exec deploy/api -n quantlix -- python -c "
import asyncio, secrets
from sqlalchemy import select
from api.db import async_session_maker
from api.email import send_verification_email
from api.models import User

async def run():
    async with async_session_maker() as s:
        r = await s.execute(select(User).where(User.email_verified==False).order_by(User.created_at.desc()).limit(2))
        for u in r.scalars().all():
            t = secrets.token_urlsafe(32)
            u.email_verification_token = t
            await s.flush()
            try:
                await send_verification_email(u.email, t)
                print('Sent to', u.email)
            except Exception as e:
                print('Failed', u.email, e)
        await s.commit()

asyncio.run(run())
"
