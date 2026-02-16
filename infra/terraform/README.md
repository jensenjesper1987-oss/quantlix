# Terraform — Infrastructure

Provisions Kubernetes cluster on Hetzner Cloud via [kube-hetzner](https://github.com/kube-hetzner/terraform-hcloud-kube-hetzner).

## Prerequisites

- [Terraform](https://www.terraform.io/downloads) >= 1.5
- [Packer](https://www.packer.io/downloads) (for MicroOS snapshots)
- [Hetzner CLI](https://github.com/hetznercloud/cli) (`brew install hcloud`)
- Hetzner Cloud account
- SSH key pair

## Usage

**Step 1: Build MicroOS snapshots** (required once; creates custom OS images)

```bash
cd infra/terraform
terraform init
export HCLOUD_TOKEN="your-64-char-hetzner-token"
./scripts/build-microos-snapshots.sh
```

This takes ~15–20 min. It creates temporary Hetzner servers, installs MicroOS, and saves snapshots.

**Step 2: Provision cluster**

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars:
# - hcloud_token: your 64-char Hetzner token
# - ssh_public_key: FULL content of ~/.ssh/id_ed25519.pub (ssh-ed25519 or ssh-rsa)
# - ssh_private_key: content of ~/.ssh/id_ed25519
# - network_region: eu-central (Europe) or us-east (US)
# - location: nbg1, fsn1, hel1 (server datacenter)

terraform plan
terraform apply

terraform output -raw kubeconfig > kubeconfig.yaml
export KUBECONFIG=$(pwd)/kubeconfig.yaml
```

## Local Development (k3d)

For local dev without Hetzner:

```bash
k3d cluster create quantlix --port 6443:6443
export KUBECONFIG=~/.kube/config
```

Then apply Kustomize manifests to the local cluster.

## GPU Node Pool (Optional)

Hetzner Cloud does not offer GPU instances. The GPU pool uses a larger CPU type (default `cpx31`) as a placeholder until real GPU is available (e.g. Hetzner dedicated GEX44, or another cloud).

To enable:

```hcl
enable_gpu    = true
gpu_node_type = "cx43"   # 8 vCPU, 16GB placeholder (cpx* deprecated)
gpu_node_count = 1
```

GPU jobs (`quantlix deploy --gpu`) are scheduled on the `workers-gpu` pool via node selector and toleration.

### Hetzner Dedicated GEX44 (Real GPU)

To add a real GPU server (Hetzner dedicated GEX44), see [docs/GPU_DEDICATED_JOIN.md](../../docs/GPU_DEDICATED_JOIN.md). Order via Robot, then manually join the node to the cluster using the k3s token (`terraform output -raw k3s_token`).
