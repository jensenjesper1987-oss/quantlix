#!/bin/bash
# Load API and Orchestrator images directly onto k3s nodes (no registry needed).
# Run from project root. Requires: docker, kubectl, SSH to nodes (root + your terraform ssh key).
#
# Node IPs: use "terraform output -json" in infra/terraform, or:
#   NODES="1.2.3.4 5.6.7.8" ./load-images-to-nodes.sh
set -e

echo "Building images..."
docker build -t quantlix-api:latest -f api/Dockerfile .
docker build -t quantlix-orchestrator:latest -f orchestrator/Dockerfile .

echo "Saving to tar..."
docker save -o /tmp/quantlix-api.tar quantlix-api:latest
docker save -o /tmp/quantlix-orchestrator.tar quantlix-orchestrator:latest

if [ -n "$NODES" ]; then
  echo "Using NODES from env: $NODES"
else
  echo "Getting node IPs..."
  if [ -d "infra/terraform" ] && command -v terraform &>/dev/null; then
    (cd infra/terraform && terraform output -json 2>/dev/null) | grep -q node_ips && {
      NODES=$(cd infra/terraform && terraform output -json 2>/dev/null | jq -r '.node_ips.value[]?' 2>/dev/null | tr '\n' ' ')
    }
  fi
  [ -z "$NODES" ] && NODES=$(kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="ExternalIP")].address}')
  [ -z "$NODES" ] && NODES=$(kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="InternalIP")].address}')
fi

if [ -z "$NODES" ]; then
  echo "No nodes found. Set NODES=ip1,ip2 or run from infra/terraform: terraform output -json | jq -r '.control_planes_public_ipv4.value[], .agents_public_ipv4.value[]'"
  exit 1
fi

for NODE in $NODES; do
  echo "Loading images on $NODE..."
  ssh -o StrictHostKeyChecking=no root@$NODE "mkdir -p /var/lib/rancher/k3s/agent/images" || {
    echo "  ssh failed. Ensure: ssh root@$NODE works (use terraform ssh key)"
    continue
  }
  scp -o StrictHostKeyChecking=no /tmp/quantlix-api.tar /tmp/quantlix-orchestrator.tar root@$NODE:/tmp/ || {
    echo "  scp failed."
    continue
  }
  ssh -o StrictHostKeyChecking=no root@$NODE 'for f in /tmp/quantlix-api.tar /tmp/quantlix-orchestrator.tar; do
    /usr/local/bin/k3s ctr images import $f 2>/dev/null || \
    /var/lib/rancher/k3s/bin/ctr -a /run/k3s/containerd/containerd.sock -n k8s.io images import $f 2>/dev/null || \
    { mkdir -p /var/lib/rancher/k3s/agent/images && cp $f /var/lib/rancher/k3s/agent/images/; }
    rm -f $f
  done'
  echo "  Done."
done

rm -f /tmp/quantlix-api.tar /tmp/quantlix-orchestrator.tar
echo ""
echo "Done. Next:"
echo "  1. Wait 30-60s for K3s to import"
echo "  2. kubectl delete deployment api orchestrator -n quantlix"
echo "  3. kubectl apply -k infra/kubernetes/overlays/prod-local"
echo ""
echo "If ErrImageNeverPull persists, load on ALL nodes (incl. workers):"
echo "  cd infra/terraform && terraform output node_ips"
echo "  NODES=\"\$(cd infra/terraform && terraform output -json node_ips 2>/dev/null | jq -r '.value[]?' | tr '\\n' ' ')\" ./infra/kubernetes/scripts/load-images-to-nodes.sh"
