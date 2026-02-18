#!/usr/bin/env python3
"""Test email sending (Sweego API or SMTP).

Usage:
  python scripts/test_smtp.py [email]   # Optional: send to this email (default: SMTP_FROM_EMAIL)
  docker compose exec api python scripts/test_smtp.py jensen.jesper1987@gmail.com
  kubectl exec deploy/api -n quantlix -- python scripts/test_smtp.py jensen.jesper1987@gmail.com
"""
import asyncio
import os
import sys

# Load .env when running locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import aiosmtplib
import httpx
from email.message import EmailMessage


async def test_api(to_email: str | None = None):
    """Test Sweego HTTP API."""
    api_key = os.getenv("SWEEGO_API_KEY", "")
    from_email = os.getenv("SMTP_FROM_EMAIL", "support@quantlix.ai")
    from_name = os.getenv("SMTP_FROM_NAME", "Quantlix")
    recipient = to_email or from_email

    auth_type = os.getenv("SWEEGO_AUTH_TYPE", "api_token")
    print("Testing Sweego API (https://api.sweego.io/send)")
    print(f"Auth type: {auth_type}")
    print(f"To: {recipient}")
    print(f"API Key: {'*' * 8 if api_key else '(not set)'} (len={len(api_key)})")
    print()

    if not api_key:
        print("ERROR: SWEEGO_API_KEY must be set in .env")
        sys.exit(1)

    payload = {
        "channel": "email",
        "provider": "sweego",
        "recipients": [{"email": recipient}],
        "from": {"name": from_name, "email": from_email},
        "subject": "Quantlix Email Test",
        "message-txt": "This is a test email from Quantlix.",
    }
    if auth_type == "bearer":
        auth_header = ("Authorization", f"Bearer {api_key}")
    elif auth_type == "api_key":
        auth_header = ("Api-Key", api_key)
    else:
        auth_header = ("Api-Token", api_key)
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://api.sweego.io/send",
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json", auth_header[0]: auth_header[1]},
        )
        if resp.status_code >= 400:
            print(f"FAILED: Sweego API returned {resp.status_code}")
            print(f"Response: {resp.text[:500]}")
            sys.exit(1)
    print("SUCCESS: Email sent successfully via Sweego API.")


async def test_smtp():
    """Test SMTP credentials."""
    host = os.getenv("SMTP_HOST", "smtp.sweego.io")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    from_email = os.getenv("SMTP_FROM_EMAIL", "support@quantlix.ai")

    print(f"Testing SMTP: {host}:{port}")
    print(f"User: {user or '(not set)'}")
    print(f"Password: {'*' * len(password) if password else '(not set)'}")
    print()

    if not user or not password:
        print("ERROR: SMTP_USER and SMTP_PASSWORD must be set in .env")
        sys.exit(1)

    msg = EmailMessage()
    msg["Subject"] = "Quantlix SMTP Test"
    msg["From"] = from_email
    msg["To"] = from_email
    msg.set_content("This is a test email from Quantlix SMTP verification.")

    await aiosmtplib.send(
        msg,
        hostname=host,
        port=port,
        username=user,
        password=password,
        start_tls=True,
    )
    print("SUCCESS: Email sent successfully. SMTP credentials are valid.")


async def main():
    to_email = sys.argv[1] if len(sys.argv) > 1 else None
    if os.getenv("SWEEGO_API_KEY"):
        await test_api(to_email)
    else:
        await test_smtp()


if __name__ == "__main__":
    asyncio.run(main())
