# Quantlix CLI — Step-by-Step Guide

## 1. Install

```bash
pip install -e .
```

## 2. Start the API (Docker)

```bash
docker compose up -d
```

## 3. Get your API key

**Option A — Sign up** (create account, verify email, then get API key):

```bash
quantlix signup --email you@example.com --password yourpassword
# Check your inbox and click the verification link, then:
quantlix verify <token-from-link>
# Or after verifying: quantlix login --email you@example.com --password yourpassword
```

**Option B — Log in** (if you already have a verified account):

```bash
quantlix login --email you@example.com --password yourpassword
```

**Option C — Dev seed** (local dev only, no password):

```bash
docker compose exec api python scripts/seed_dev.py
```

Copy the printed API key and set it in step 4.

## 4. Set your API key

**Required.** All deploy, run, and status commands need an API key. Add to `.env` or export in your shell:

```bash
export QUANTLIX_API_KEY="dev-api-key-xxxxxxxx"
```

Or pass it per command: `quantlix deploy my-model --api-key qxl_xxx`

**Local dev only** (default is `https://api.quantlix.ai`):

```bash
export QUANTLIX_API_URL="http://localhost:8000"
```

## 5. Deploy a model

```bash
quantlix deploy my-model
```

You'll get a `deployment_id` — copy it. The deployment starts as `pending`.

## 6. Run inference

**Trigger a run to activate the deployment.** The first run moves the deployment from `pending` to `ready`:

```bash
quantlix run <deployment_id> -i '{"prompt": "Hello world"}'
```

Or from a JSON file:

```bash
echo '{"prompt": "Hello"}' > input.json
quantlix run <deployment_id> -i input.json
```

You'll get a `job_id`.

## 7. Check status

```bash
quantlix status <deployment_id>   # or <job_id>
```

Deployments show `pending` until the first run completes; then they become `ready`.

## 8. View usage

```bash
quantlix usage
quantlix usage --start 2025-01-01 --end 2025-02-14
```

Usage limits (tokens, compute seconds per month) can be configured via env vars. When limits are reached, `quantlix run` returns an error.

---

**Quick reference**

| Command | Example |
|---------|---------|
| `quantlix signup` | `quantlix signup -e you@example.com -p secret` |
| `quantlix verify` | `quantlix verify <token-from-email>` |
| `quantlix login` | `quantlix login -e you@example.com -p secret` |
| `quantlix forgot-password` | `quantlix forgot-password -e you@example.com` |
| `quantlix reset-password` | `quantlix reset-password <token> -p newpassword` |
| `quantlix api-keys` | List your API keys |
| `quantlix create-api-key` | Create a new API key |
| `quantlix revoke-api-key` | Revoke an API key by ID |
| `quantlix rotate-api-key` | Create new key, revoke current |
| `quantlix deploy <model_id>` | `quantlix deploy llama-7b` (needs API key) |
| `quantlix run <deployment_id> -i <json>` | `quantlix run abc123 -i '{"prompt":"Hi"}'` (triggers first run → deployment becomes ready) |
| `quantlix status <id>` | `quantlix status abc123` |
| `quantlix usage` | `quantlix usage` |
