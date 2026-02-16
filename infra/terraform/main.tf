# -----------------------------------------------------------------------------
# Quantlix — Infrastructure
# Hetzner Cloud + kube-hetzner (k3s-based K8s cluster)
# -----------------------------------------------------------------------------

provider "hcloud" {
  token = var.hcloud_token
}

locals {
  # Extract first valid SSH public key line (handles comment lines, multi-line files)
  raw_public_key  = var.ssh_public_key_path != "" ? file(pathexpand(var.ssh_public_key_path)) : var.ssh_public_key
  key_lines       = [for line in split("\n", local.raw_public_key) : trimspace(line) if trimspace(line) != "" && !startswith(trimspace(line), "#")]
  ssh_public_key  = length(local.key_lines) > 0 ? local.key_lines[0] : trimspace(local.raw_public_key)
  ssh_private_key = var.ssh_private_key_path != "" ? file(pathexpand(var.ssh_private_key_path)) : var.ssh_private_key
}

module "kube_hetzner" {
  source  = "kube-hetzner/kube-hetzner/hcloud"
  version = "~> 2.17"

  providers = {
    hcloud = hcloud
  }

  cluster_name = var.cluster_name

  # Credentials (use *_path to read from file and avoid copy-paste issues)
  hcloud_token    = var.hcloud_token
  ssh_public_key  = local.ssh_public_key
  ssh_private_key = local.ssh_private_key

  # Networking (network_zone: eu-central for Europe, us-east for US)
  network_region = var.network_region

  # Control plane (single node for MVP; use 3 for HA)
  control_plane_nodepools = [
    {
      name        = "control-plane"
      server_type = var.node_type
      location    = var.location
      labels      = []
      taints      = []
      count       = 1
    }
  ]

  # Worker nodes (CPU) + optional GPU pool
  # Note: Hetzner Cloud has no GPU instances. Use cx33/cx43 as placeholder until real GPU
  # (e.g. Hetzner dedicated GEX44 or another cloud). Jobs with config.gpu target this pool.
  agent_nodepools = concat(
    [
      {
        name        = "workers"
        server_type = var.node_type
        location    = var.location
        labels      = []
        taints      = []
        count       = var.node_count
      }
    ],
    var.enable_gpu && var.gpu_node_count > 0 ? [
      {
        name        = "workers-gpu"
        server_type = var.gpu_node_type
        location    = var.gpu_location != "" ? var.gpu_location : var.location
        labels      = ["quantlix.com/gpu=true"]
        taints      = ["nvidia.com/gpu=true:NoSchedule"]
        count       = var.gpu_node_count
      }
    ] : []
  )

  # Load balancer (required by module)
  load_balancer_type     = "lb11"
  load_balancer_location = var.location
}

variable "hcloud_token" {
  description = "Hetzner Cloud API token"
  type        = string
  sensitive   = true
}

variable "ssh_public_key" {
  description = "SSH public key content (or use ssh_public_key_path instead)"
  type        = string
  default     = ""
}

variable "ssh_private_key" {
  description = "SSH private key content (or use ssh_private_key_path instead)"
  type        = string
  sensitive   = true
  default     = ""
}
