# API — Build & Deploy Step-by-Step

## Option A: Local development (Docker)

### 1. Prerequisites

- Docker installed
- `.env` file (copy from `.env.example` and fill in values)

```bash
cp .env.example .env
# Edit .env — at minimum set JWT_SECRET (openssl rand -hex 32)
```

### 2. Build the API image

```bash
docker build -t quantlix-api:latest -f api/Dockerfile .
```

### 3. Run with dependencies

The API needs PostgreSQL, Redis, and MinIO. Use one of:

**A) Docker Compose** (if you have a `docker-compose.yml`):

```bash
docker compose up -d
```

**B) Run API only** (when Postgres, Redis, MinIO are already running):

```bash
docker run -p 8000:8000 --env-file .env \
  -e POSTGRES_HOST=host.docker.internal \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  -e MINIO_ENDPOINT=host.docker.internal:9000 \
  quantlix-api:latest
```

**C) Run with uvicorn** (no Docker, for quick dev):

```bash
pip install -e ".[full]"
# Ensure Postgres, Redis, MinIO are running
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Verify

```bash
curl http://localhost:8000/
# {"service":"quantlix","version":"0.1.0"}

curl -X POST http://localhost:8000/demo -H "Content-Type: application/json" -d '{"prompt":"Hello"}'
```

---

## Option B: Kubernetes (production)

### 1. Prerequisites

- `kubectl` configured for your cluster
- Docker (for building)
- Docker Hub account (or another registry)

### 2. Build the API image

```bash
docker build -t quantlix-api:latest -f api/Dockerfile .
```

### 3. Tag and push to registry

```bash
# Replace jesperjensen888 with your Docker Hub username
docker tag quantlix-api:latest docker.io/jesperjensen888/quantlix-api:latest
docker login
docker push docker.io/jesperjensen888/quantlix-api:latest
```

### 4. Update Kustomize overlay (if using a different registry)

Edit `infra/kubernetes/overlays/prod/kustomization.yaml`:

```yaml
images:
  - name: quantlix-api:latest
    newName: docker.io/YOUR_USERNAME/quantlix-api
    newTag: latest
```

### 5. Ensure secrets exist

The API deployment expects these secrets in the `quantlix` namespace:

- `postgres` — `username`, `password`
- `minio` — `access-key`, `secret-key`
- `api` — `jwt-secret`, and optionally: `sweego-api-key`, `stripe-secret-key`, etc.

Create them if needed:

```bash
kubectl create secret generic postgres -n quantlix \
  --from-literal=username=cloud \
  --from-literal=password=YOUR_SECURE_PASSWORD

kubectl create secret generic minio -n quantlix \
  --from-literal=access-key=minioadmin \
  --from-literal=secret-key=YOUR_MINIO_SECRET

kubectl create secret generic api -n quantlix \
  --from-literal=jwt-secret=$(openssl rand -hex 32)
```

### 6. Deploy

```bash
kubectl apply -k infra/kubernetes/overlays/prod
```

### 7. Verify

```bash
kubectl get pods -n quantlix
kubectl get ingress -n quantlix

# If ingress is configured for api.quantlix.ai:
curl https://api.quantlix.ai/
curl -X POST https://api.quantlix.ai/demo -H "Content-Type: application/json" -d '{"prompt":"Hello"}'
```

---

## Option C: Local k3d (no registry)

For local Kubernetes without pushing to a registry:

### 1. Create cluster

```bash
k3d cluster create quantlix --port 6443:6443
export KUBECONFIG=~/.kube/config
```

### 2. Build images

```bash
docker build -t quantlix-api:latest -f api/Dockerfile .
docker build -t quantlix-orchestrator:latest -f orchestrator/Dockerfile .
docker build -t quantlix-inference:latest -f inference/Dockerfile .
```

### 3. Import into k3d

```bash
k3d image import quantlix-api:latest quantlix-orchestrator:latest quantlix-inference:latest -c quantlix
```

### 4. Deploy (use dev overlay)

```bash
kubectl apply -k infra/kubernetes/overlays/dev
```

### 5. Port-forward to access API

```bash
kubectl port-forward svc/api 8000:8000 -n quantlix
# API at http://localhost:8000
```

---

## Quick reference

| Step              | Command |
|-------------------|---------|
| Build API image   | `docker build -t quantlix-api:latest -f api/Dockerfile .` |
| Run API (uvicorn) | `uvicorn api.main:app --host 0.0.0.0 --port 8000` |
| Push to registry | `docker tag quantlix-api:latest docker.io/USER/quantlix-api:latest && docker push ...` |
| Deploy to K8s    | `kubectl apply -k infra/kubernetes/overlays/prod` |
| Health check     | `curl http://localhost:8000/health` |
