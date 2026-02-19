# Troubleshooting ImagePullBackOff

## 1. Verify which image the cluster is using

```bash
kubectl get deployment api -n quantlix -o jsonpath='{.spec.template.spec.containers[0].image}'
```

**Expected:** `docker.io/jesperjensen888/quantlix-api:latest`

If you see `quantlix-api:latest` (no registry), the **prod overlay is not applied**. Run:

```bash
kubectl apply -k infra/kubernetes/overlays/prod
```

## 2. Verify images exist on Docker Hub

Check these URLs (replace username if different):

- https://hub.docker.com/r/jesperjensen888/quantlix-api/tags
- https://hub.docker.com/r/jesperjensen888/quantlix-orchestrator/tags
- https://hub.docker.com/r/jesperjensen888/quantlix-inference/tags

Each should show `latest` tag. If not, push again:

```bash
docker push docker.io/jesperjensen888/quantlix-api:latest
docker push docker.io/jesperjensen888/quantlix-orchestrator:latest
docker push docker.io/jesperjensen888/quantlix-inference:latest
```

## 3. Private Docker Hub repo — add imagePullSecrets

If your Docker Hub repo is **private**, create a pull secret:

```bash
kubectl create secret docker-registry dockerhub-pull \
  --docker-server=docker.io \
  --docker-username=jesperjensen888 \
  --docker-password=YOUR_DOCKERHUB_TOKEN_OR_PASSWORD \
  -n quantlix \
  --dry-run=client -o yaml | kubectl apply -f -
```

Then add `imagePullSecrets` to the API and orchestrator deployments. The base manifests don't include this; you'd need to patch them.

## 4. Force clean rollout

If you have multiple ReplicaSets and stale pods:

```bash
# Delete deployments (pods will be recreated from apply)
kubectl delete deployment api orchestrator -n quantlix

# Re-apply
kubectl apply -k infra/kubernetes/overlays/prod
```

## 5. "no match for platform in manifest" — wrong architecture

You built on Mac (arm64) but cluster nodes are amd64 (x86_64). Rebuild for the target platform:

```bash
docker build --platform linux/amd64 -t quantlix-api:latest -f api/Dockerfile .
docker build --platform linux/amd64 -t quantlix-orchestrator:latest -f orchestrator/Dockerfile .
docker build --platform linux/amd64 -t quantlix-inference:latest -f inference/Dockerfile .
```

Then tag, push, and restart as usual.

## 6. Check the exact pull error

```bash
kubectl describe pod -n quantlix -l app=api | tail -20
```

Look for:
- `no match for platform in manifest` → Wrong architecture; rebuild with `--platform linux/amd64`
- `repository does not exist` → Image not pushed or wrong name
- `authorization failed` / `pull access denied` → Private repo, need imagePullSecrets
- `not found` → Wrong tag
