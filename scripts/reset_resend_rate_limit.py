#!/usr/bin/env python3
"""Reset resend verification rate limit for an email.

Usage:
  # Local (with REDIS_URL in .env or env):
  python scripts/reset_resend_rate_limit.py jensen.jesper1987@gmail.com

  # From inside K8s API pod:
  kubectl exec deploy/api -n quantlix -- python scripts/reset_resend_rate_limit.py jensen.jesper1987@gmail.com
"""
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import redis


def _email_key_safe(email: str) -> str:
    return email.strip().lower().replace("@", "_at_")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/reset_resend_rate_limit.py <email|--all>")
        print("  email  - Reset for specific email only")
        print("  --all  - Reset ALL resend limits (use when portal shares IP e.g. Vercel)")
        print("Example: python scripts/reset_resend_rate_limit.py jensen.jesper1987@gmail.com")
        sys.exit(1)

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    r = redis.from_url(redis_url)

    if sys.argv[1] == "--all":
        keys = r.keys("rate_limit:auth:resend:*")
        if keys:
            deleted = r.delete(*keys)
            print(f"Reset {deleted} resend rate limit key(s)")
        else:
            print("No resend rate limit keys found")
    else:
        email = sys.argv[1]
        key = f"rate_limit:auth:resend:email:{_email_key_safe(email)}"
        deleted = r.delete(key)
        if deleted:
            print(f"Reset email limit for {email}. If still 429, run with --all (IP may be shared).")
        else:
            print(f"No email key for {email}. Try --all to reset all limits.")

    r.close()


if __name__ == "__main__":
    main()
