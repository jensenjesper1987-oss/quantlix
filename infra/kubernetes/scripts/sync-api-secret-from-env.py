#!/usr/bin/env python3
"""
Sync api secret from .env to Kubernetes.
Usage: python infra/kubernetes/scripts/sync-api-secret-from-env.py
       (run from project root)
Reads JWT_SECRET, SWEEGO_API_KEY, SMTP_USER, SMTP_PASSWORD from .env and creates/updates the api secret.
Use SWEEGO_API_KEY for Sweego HTTP API (recommended in K8s; avoids SMTP port blocking).
"""
import os
import subprocess
import sys

# Project root (parent of infra/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
NAMESPACE = os.environ.get("NAMESPACE", "quantlix")


def main():
    if not os.path.exists(ENV_FILE):
        print(f"Error: .env not found at {ENV_FILE}", file=sys.stderr)
        sys.exit(1)

    # Load .env
    env = {}
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                env[key] = val

    jwt_secret = env.get("JWT_SECRET")
    email_enabled = env.get("EMAIL_ENABLED", "true").lower() in ("true", "1", "yes")
    sweego_api_key = env.get("SWEEGO_API_KEY", "")
    sweego_auth_type = env.get("SWEEGO_AUTH_TYPE", "api_token")
    smtp_user = env.get("SMTP_USER", "")
    smtp_password = env.get("SMTP_PASSWORD", "")

    if not jwt_secret:
        print("Error: JWT_SECRET not set in .env", file=sys.stderr)
        sys.exit(1)

    print(f"Syncing api secret to namespace {NAMESPACE}...")

    result = subprocess.run(
        [
            "kubectl", "create", "secret", "generic", "api",
            "-n", NAMESPACE,
            "--from-literal=jwt-secret=" + jwt_secret,
            "--from-literal=email-enabled=" + ("true" if email_enabled else "false"),
            "--from-literal=sweego-api-key=" + sweego_api_key,
            "--from-literal=sweego-auth-type=" + sweego_auth_type,
            "--from-literal=smtp-user=" + smtp_user,
            "--from-literal=smtp-password=" + smtp_password,
            "--dry-run=client", "-o", "yaml",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    apply = subprocess.run(
        ["kubectl", "apply", "-f", "-"],
        input=result.stdout,
        capture_output=True,
        text=True,
    )
    if apply.returncode != 0:
        print(apply.stderr, file=sys.stderr)
        sys.exit(apply.returncode)

    print("Secret updated. Restarting API deployment...")
    subprocess.run(
        ["kubectl", "rollout", "restart", "deploy/api", "-n", NAMESPACE],
        check=True,
    )
    subprocess.run(
        ["kubectl", "rollout", "status", "deploy/api", "-n", NAMESPACE, "--timeout=120s"],
        check=True,
    )
    print("Done.")


if __name__ == "__main__":
    main()
