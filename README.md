# Quantlix

Deploy AI models in seconds. A simple inference platform with REST API, usage-based billing, and Kubernetes orchestration.

## Features

- **REST API** — Deploy models, run inference, check status
- **Usage-based billing** — Free, Starter (€9/mo), Pro (€19/mo) tiers with Stripe
- **Queue & orchestration** — Redis queue, K8s job scheduling
- **Customer portal** — Next.js dashboard, usage graphs, real-time logs
- **CLI** — `quantlix deploy`, `quantlix run` for local dev

## Quick start

```bash
# 1. Clone and start services
git clone https://github.com/quantlix/cloud
cd cloud
cp .env.example .env
docker compose up -d

# 2. Create account and get API key
pip install -e .
quantlix signup --email you@example.com --password YourSecurePassword123!
# Verify email, then:
quantlix login --email you@example.com --password YourSecurePassword123!
# Set the API key (required for deploy/run):
export QUANTLIX_API_KEY="qxl_xxx"  # from login output

# 3. Deploy and run
quantlix deploy qx-example
# Run inference to activate (first run moves deployment from pending to ready)
quantlix run <deployment_id> -i '{"prompt": "Hello!"}'
```

See [docs/CLI_GUIDE.md](docs/CLI_GUIDE.md) for detailed setup.

## Architecture

```
┌─────────────┐     ┌─────────┐     ┌──────────────┐
│   Portal    │────▶│   API   │────▶│  PostgreSQL  │
│  (Next.js)  │     │(FastAPI)│     │    Redis     │
└─────────────┘     └────┬────┘     └──────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Orchestrator │────▶ Kubernetes / Inference
                  │  (Worker)    │
                  └──────────────┘
```

## Project structure

| Directory | Description |
|-----------|-------------|
| `api/` | FastAPI backend (auth, deploy, run, billing, usage) |
| `portal/` | Next.js customer dashboard |
| `orchestrator/` | Redis queue worker, K8s job runner |
| `inference/` | Mock inference service (replace with your model server) |
| `sdk/` | Python client library |
| `cli/` | `quantlix` CLI |
| `infra/` | Terraform (Hetzner), Kubernetes manifests |

## Production

See [docs/GO_LIVE.md](docs/GO_LIVE.md) for the full deployment checklist: Stripe, SMTP, DNS, SSL, secrets.

## License

MIT — see [LICENSE](LICENSE).
