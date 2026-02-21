# Deploy Guardrails to Prod & Test Cost Visibility

Step-by-step guide to deploy your guardrails, scoring, and cost visibility changes to production, then run the cost visibility test against `api.quantlix.ai`.

---

## Prerequisites

- Docker installed and logged in to Docker Hub
- `kubectl` configured for your production cluster
- Access to the `quantlix` namespace

---

## Step 1: Commit your changes

```bash
git status   # Ensure guardrails, scoring, policies, usage changes are staged
git add -A
git commit -m "Add guardrails, scoring, policies, cost visibility"
```

---

## Step 2: Build images for production

Production nodes are typically `linux/amd64`. Build for that platform:

```bash
cd /path/to/cloud

docker build --platform linux/amd64 -t quantlix-api:latest -f api/Dockerfile .
docker build --platform linux/amd64 -t quantlix-orchestrator:latest -f orchestrator/Dockerfile .
docker build --platform linux/amd64 -t quantlix-inference:latest -f inference/Dockerfile .
```

---

## Step 3: Tag for Docker Hub

```bash
REGISTRY="docker.io/jesperjensen888"   # or your Docker Hub username

docker tag quantlix-api:latest ${REGISTRY}/quantlix-api:latest
docker tag quantlix-orchestrator:latest ${REGISTRY}/quantlix-orchestrator:latest
docker tag quantlix-inference:latest ${REGISTRY}/quantlix-inference:latest
```

---

## Step 4: Push to Docker Hub

```bash
docker login   # if not already logged in

docker push ${REGISTRY}/quantlix-api:latest
docker push ${REGISTRY}/quantlix-orchestrator:latest
docker push ${REGISTRY}/quantlix-inference:latest
```

---

## Step 5: Apply Kubernetes manifests and restart

```bash
kubectl apply -k infra/kubernetes/overlays/prod

kubectl rollout restart deployment api orchestrator -n quantlix
kubectl rollout status deployment api -n quantlix --timeout=120s
```

---

## Step 6: Verify deployment

```bash
kubectl get pods -n quantlix -l app=api
kubectl get pods -n quantlix -l app=orchestrator
```

Both should show `Running` and `1/1` or `2/2` Ready.

Optional: check API health:

```bash
curl -s https://api.quantlix.ai/health | jq
```

---

## Step 7: Run cost visibility test against prod

```bash
export QUANTLIX_API_URL="https://api.quantlix.ai"
export QUANTLIX_API_KEY="dev-api-key-fa77c32b"

./scripts/test_cost_visibility_retries.sh
```

The script will:

1. Create a deployment with strict policy (or use an existing one)
2. Record baseline usage
3. Run 2 requests that get blocked (PII → policy block)
4. Run 1 request that succeeds
5. Verify: `job_count` +1, `blocked_jobs_count` +2

---

## One-liner (using deploy-prod.sh)

If you already have `scripts/deploy-prod.sh`:

```bash
./scripts/deploy-prod.sh
```

Then run the test:

```bash
export QUANTLIX_API_URL="https://api.quantlix.ai"
export QUANTLIX_API_KEY="dev-api-key-fa77c32b"
./scripts/test_cost_visibility_retries.sh
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ImagePullBackOff` | See [docs/TROUBLESHOOT_IMAGEPULL.md](TROUBLESHOOT_IMAGEPULL.md) |
| `no match for platform` | Rebuild with `--platform linux/amd64` |
| Deploy fails (401/403) | Check API key is valid for prod |
| Test script gets empty deployment | Pass deployment ID: `./scripts/test_cost_visibility_retries.sh $API_KEY <deployment_id>` |
| Orchestrator not processing jobs | `kubectl logs deploy/orchestrator -n quantlix --tail=50` |
