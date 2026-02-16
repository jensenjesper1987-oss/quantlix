# Development Guide

## Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local CLI/SDK dev)
- (Optional) k3d or kind for local Kubernetes

## Local Setup

```bash
# Clone and enter project
cd cloud

# Copy environment
cp .env.example .env

# Start all services
docker compose up -d

# Seed dev user + API key (run once, inside API container)
docker compose exec api python scripts/seed_dev.py
# Use the printed API key in X-API-Key header for all API calls

# Check services
docker compose ps
```

## Service URLs

| Service     | URL                    | Notes                    |
|-------------|------------------------|--------------------------|
| API         | http://localhost:8000  | FastAPI, /docs for Swagger |
| Inference   | http://localhost:8081  | DistilGPT2 text generation |
| Grafana     | http://localhost:3000  | admin/admin              |
| Prometheus  | http://localhost:9090  |                          |
| MinIO       | http://localhost:9001  | Console, minioadmin/minioadmin |
| Traefik     | http://localhost:8080  | Dashboard (profile: full) |

## Running API Locally (without Docker)

```bash
# Create venv
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install deps
pip install -r api/requirements.txt

# Set env (use localhost for postgres, redis)
export POSTGRES_HOST=localhost REDIS_URL=redis://localhost:6379/0

# Run
uvicorn api.main:app --reload --port 8000
```

## Orchestrator & Inference

The orchestrator consumes jobs from Redis and runs inference via:

- **Local dev** (`MOCK_K8S=true`): Calls the inference HTTP service at `INFERENCE_URL` (default `http://inference:8080`)
- **Real K8s**: Creates K8s Jobs using the `quantlix-inference` image; containers write results to Redis

The **inference container** runs DistilGPT2 for text generation:

- **Server mode** (docker-compose): HTTP API on port 8080, used when `MOCK_K8S=true`
- **Job mode** (K8s): One-shot per job, reads `JOB_ID`/`INPUT`/`REDIS_URL`, writes result to Redis

Build the inference image: `docker compose build inference`

## Adding Kubernetes (Local)

For orchestrator development with real K8s:

```bash
# Create k3d cluster
k3d cluster create cloud --port 6443:6443

# Export kubeconfig
export KUBECONFIG=~/.kube/config

# Set MOCK_K8S=false in .env for orchestrator
```

## Infrastructure as Code

### Terraform (Hetzner Cloud)

kube-hetzner requires MicroOS snapshots. Build them first (once, ~15–20 min):

```bash
cd infra/terraform
terraform init
export HCLOUD_TOKEN="PA8XHoWYRQkLn2buRheScn3E69rS0jOKzPlGloOzTPt61YqbhOtslL9gle2fHTUg"
./scripts/build-microos-snapshots.sh
```

Then provision the cluster:

```bash
cp terraform.tfvars.example terraform.tfvars  # Add hcloud_token, SSH keys
terraform apply
terraform output -raw kubeconfig > kubeconfig.yaml
export KUBECONFIG=$(pwd)/kubeconfig.yaml
```

### Kustomize (K8s Workloads)

```bash
# Build images
make build

# Deploy to cluster
make deploy-dev   # or deploy-prod
```

See [infra/kubernetes/README.md](../infra/kubernetes/README.md) for details.

## CLI

```bash
# Install: pip install -e .
export QUANTLIX_API_KEY="your-api-key"   # or use --api-key

quantlix deploy my-llama-7b
quantlix run <deployment_id> -i '{"prompt": "Hello"}'
quantlix status <deployment_id_or_job_id>
quantlix usage
```

## Project Structure

```
api/           → FastAPI app, routes, config
orchestrator/  → Queue worker, K8s client
inference/     → Model container (DistilGPT2), HTTP + Job modes
cli/           → Typer CLI (deploy, run, status, usage)
sdk/quantlix/  → Python SDK (QuantlixCloudClient)
sdk/js/        → JS/TS SDK (@quantlix/sdk)
infra/         → Terraform, K8s, Prometheus, Grafana
model-base/    → Base Dockerfile for custom models
```
