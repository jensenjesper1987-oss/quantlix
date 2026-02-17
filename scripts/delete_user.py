#!/usr/bin/env python3
"""
Delete a user and all related data (api_keys, deployments, jobs, usage_records).
Usage: python scripts/delete_user.py <email>
Env: POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB (or use .env)

For prod via port-forward: POSTGRES_HOST=localhost + kubectl port-forward svc/postgres 5432:5432 -n quantlix
"""
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def _get_sync_url() -> str:
    """Build sync postgres URL from env (no api.config dependency)."""
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    user = os.environ.get("POSTGRES_USER", "cloud")
    password = os.environ.get("POSTGRES_PASSWORD", "cloud_secret")
    db = os.environ.get("POSTGRES_DB", "cloud")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def delete_user(email: str) -> bool:
    engine = create_engine(_get_sync_url(), echo=False)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    with Session() as session:
        result = session.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
        row = result.fetchone()
        if not row:
            print(f"User not found: {email}")
            return False

        user_id = row[0]
        print(f"Deleting user {email} (id={user_id})...")

        # Delete in order (respect FK constraints)
        session.execute(text("DELETE FROM usage_records WHERE user_id = :uid"), {"uid": user_id})
        session.execute(text("DELETE FROM jobs WHERE user_id = :uid"), {"uid": user_id})
        session.execute(text("DELETE FROM deployments WHERE user_id = :uid"), {"uid": user_id})
        session.execute(text("DELETE FROM api_keys WHERE user_id = :uid"), {"uid": user_id})
        session.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": user_id})

        session.commit()
        print("User deleted.")
        return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/delete_user.py <email>")
        sys.exit(1)
    email = sys.argv[1].strip()
    ok = delete_user(email)
    sys.exit(0 if ok else 1)
