#!/usr/bin/env python3
"""
Sync api secret from .env to Kubernetes.
Usage: python infra/kubernetes/scripts/sync-api-secret-from-env.py
       (run from project root)
Reads JWT_SECRET, SWEEGO_API_KEY, SMTP_USER, SMTP_PASSWORD, Stripe keys from .env and creates/updates the api secret.
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
    # Verify kubectl can reach cluster
    check = subprocess.run(
        ["kubectl", "cluster-info"],
        capture_output=True,
        text=True,
    )
    if check.returncode != 0:
        print("Error: kubectl cannot reach the cluster. Set KUBECONFIG to your cluster config, e.g.:", file=sys.stderr)
        print("  export KUBECONFIG=$(pwd)/infra/terraform/kubeconfig.yaml", file=sys.stderr)
        sys.exit(1)

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
    stripe_secret_key = env.get("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret = env.get("STRIPE_WEBHOOK_SECRET", "")
    stripe_price_id_starter = env.get("STRIPE_PRICE_ID_STARTER", "")
    stripe_price_id_pro = env.get("STRIPE_PRICE_ID_PRO", "")

    if not jwt_secret:
        print("Error: JWT_SECRET not set in .env", file=sys.stderr)
        sys.exit(1)

    if not stripe_secret_key or not stripe_price_id_starter or not stripe_price_id_pro:
        print("Warning: Stripe keys missing or empty in .env:", file=sys.stderr)
        if not stripe_secret_key:
            print("  - STRIPE_SECRET_KEY", file=sys.stderr)
        if not stripe_price_id_starter:
            print("  - STRIPE_PRICE_ID_STARTER", file=sys.stderr)
        if not stripe_price_id_pro:
            print("  - STRIPE_PRICE_ID_PRO", file=sys.stderr)
        print("Billing will not work until these are set.", file=sys.stderr)

    print(f"Syncing api secret to namespace {NAMESPACE}...")

    literals = [
        "jwt-secret=" + jwt_secret,
        "email-enabled=" + ("true" if email_enabled else "false"),
        "sweego-api-key=" + sweego_api_key,
        "sweego-auth-type=" + sweego_auth_type,
        "smtp-user=" + smtp_user,
        "smtp-password=" + smtp_password,
        "stripe-secret-key=" + stripe_secret_key,
        "stripe-webhook-secret=" + stripe_webhook_secret,
        "stripe-price-id-starter=" + stripe_price_id_starter,
        "stripe-price-id-pro=" + stripe_price_id_pro,
    ]
    result = subprocess.run(
        [
            "kubectl", "create", "secret", "generic", "api",
            "-n", NAMESPACE,
            *[f"--from-literal={l}" for l in literals],
            "--dry-run=client", "-o", "yaml",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    apply = subprocess.run(
        ["kubectl", "apply", "-f", "-", "--validate=false"],
        input=result.stdout,
        capture_output=True,
        text=True,
    )
    if apply.returncode != 0:
        print(apply.stderr, file=sys.stderr)
        sys.exit(apply.returncode)

    print("Secret updated. Stripe keys:", "OK" if (stripe_secret_key and stripe_price_id_starter and stripe_price_id_pro) else "MISSING (check .env)")
    print("Restarting API deployment...")
    subprocess.run(
        ["kubectl", "rollout", "restart", "deploy/api", "-n", NAMESPACE],
        check=True,
    )
    subprocess.run(
        ["kubectl", "rollout", "status", "deploy/api", "-n", NAMESPACE, "--timeout=120s"],
        check=True,
    )
    print("Done.")
    print("If billing still fails, ensure the deployment is applied: kubectl apply -k infra/kubernetes/overlays/prod")


if __name__ == "__main__":
    main()
