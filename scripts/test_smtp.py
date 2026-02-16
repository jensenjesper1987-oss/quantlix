#!/usr/bin/env python3
"""Test SMTP credentials. Run: docker compose exec api python scripts/test_smtp.py"""
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
from email.message import EmailMessage


async def main():
    host = os.getenv("SMTP_HOST", "smtp.heysender.com")
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
    msg["To"] = from_email  # Send to self for test
    msg.set_content("This is a test email from Quantlix SMTP verification.")

    try:
        await aiosmtplib.send(
            msg,
            hostname=host,
            port=port,
            username=user,
            password=password,
            start_tls=True,
        )
        print("SUCCESS: Email sent successfully. SMTP credentials are valid.")
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
