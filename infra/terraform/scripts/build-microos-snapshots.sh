#!/usr/bin/env bash
# Build MicroOS snapshots for kube-hetzner (required before terraform apply)
# Requires: packer, hcloud CLI, HCLOUD_TOKEN env var

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(dirname "$SCRIPT_DIR")"
PACKER_FILE="$TERRAFORM_DIR/.terraform/modules/kube_hetzner/packer-template/hcloud-microos-snapshots.pkr.hcl"

if [ -z "$HCLOUD_TOKEN" ]; then
  echo "Error: HCLOUD_TOKEN must be set (your Hetzner Cloud API token)"
  exit 1
fi

if [ ! -f "$PACKER_FILE" ]; then
  echo "Error: Run 'terraform init' first to download the kube-hetzner module"
  exit 1
fi

echo "Building MicroOS snapshots (x86 + ARM)..."
echo "This creates temporary Hetzner servers and takes ~15-20 minutes."
cd "$(dirname "$PACKER_FILE")"
packer init hcloud-microos-snapshots.pkr.hcl
packer build hcloud-microos-snapshots.pkr.hcl
echo "Done. You can now run 'terraform apply' in $TERRAFORM_DIR"
