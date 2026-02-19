#!/bin/bash
# Deploy Quantlix API + Orchestrator + Inference to production (remote cluster).
# Prerequisites: docker, kubectl, Docker Hub login.
set -e

REGISTRY="docker.io/jesperjensen888"

echo "1. Building images (linux/amd64 for cluster nodes)..."
docker build --platform linux/amd64 -t quantlix-api:latest -f api/Dockerfile .
docker build --platform linux/amd64 -t quantlix-orchestrator:latest -f orchestrator/Dockerfile .
docker build --platform linux/amd64 -t quantlix-inference:latest -f inference/Dockerfile .

echo "2. Tagging for registry..."
docker tag quantlix-api:latest ${REGISTRY}/quantlix-api:latest
docker tag quantlix-orchestrator:latest ${REGISTRY}/quantlix-orchestrator:latest
docker tag quantlix-inference:latest ${REGISTRY}/quantlix-inference:latest

echo "3. Pushing to Docker Hub..."
docker push ${REGISTRY}/quantlix-api:latest
docker push ${REGISTRY}/quantlix-orchestrator:latest
docker push ${REGISTRY}/quantlix-inference:latest

echo "4. Applying prod overlay..."
kubectl apply -k infra/kubernetes/overlays/prod

echo "5. Forcing fresh rollout (clears stale ReplicaSets)..."
kubectl rollout restart deployment api orchestrator -n quantlix
kubectl rollout status deployment api -n quantlix --timeout=120s || true

echo ""
echo "Done. Check status with:"
echo "  kubectl get pods -n quantlix"
echo "  kubectl rollout status deployment api -n quantlix"
