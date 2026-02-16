# Kubernetes — Kustomize Manifests

Deploy Quantlix to Kubernetes.

## Prerequisites

- `kubectl` configured for your cluster
- Images built and pushed (or use local images with k3d)

## Quick Start (Local k3d)

```bash
# Create cluster
k3d cluster create quantlix --port 6443:6443
export KUBECONFIG=~/.kube/config

# Build images
docker build -t quantlix-api:latest -f api/Dockerfile .
docker build -t quantlix-orchestrator:latest -f orchestrator/Dockerfile .
docker build -t quantlix-inference:latest -f inference/Dockerfile .

# Load into k3d (optional, for local images)
k3d image import quantlix-api:latest quantlix-orchestrator:latest quantlix-inference:latest -c quantlix

# Deploy
kubectl apply -k infra/kubernetes/overlays/dev
```

## Overlays

| Overlay | Use Case |
|---------|----------|
| `overlays/dev` | Local/dev cluster, mock K8s, single replica |
| `overlays/prod` | Production, real K8s, scaled replicas |

## Deploy

```bash
# Dev
kubectl apply -k infra/kubernetes/overlays/dev

# Prod (after setting images in kustomization.yaml)
kubectl apply -k infra/kubernetes/overlays/prod
```

## Structure

```
base/
├── namespace.yaml
├── postgres/      # StatefulSet + Service + Secret
├── redis/         # Deployment + Service
├── minio/         # Deployment + PVC + Service + Secret
├── api/           # Deployment + Service + Secret
├── orchestrator/  # Deployment + Service
├── prometheus/    # ConfigMap + Deployment + Service
├── grafana/       # Deployment + ConfigMap + Secret + Service
└── ingress.yaml   # Ingress for API + Grafana

overlays/
├── dev/           # Local images, MOCK_K8S=true
└── prod/          # Registry images, MOCK_K8S=false, scaled
```
