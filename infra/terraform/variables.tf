variable "ssh_public_key_path" {
  description = "Path to SSH public key file (e.g. ~/.ssh/id_ed25519.pub). Use this instead of ssh_public_key to avoid formatting issues."
  type        = string
  default     = ""
}

variable "ssh_private_key_path" {
  description = "Path to SSH private key file (e.g. ~/.ssh/id_ed25519). Use this instead of ssh_private_key to avoid formatting issues."
  type        = string
  default     = ""
}

variable "cluster_name" {
  description = "Kubernetes cluster name"
  type        = string
  default     = "quantlix"
}

variable "location" {
  description = "Hetzner location for servers (nbg1, fsn1, hel1, etc.)"
  type        = string
  default     = "nbg1"
}

variable "network_region" {
  description = "Hetzner network zone (eu-central for Europe, us-east for US)"
  type        = string
  default     = "eu-central"
}

variable "k8s_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.29"
}

variable "node_type" {
  description = "Hetzner node type (cx23 = 2 vCPU, 4GB min for k3s)"
  type        = string
  default     = "cx23"
}

variable "node_count" {
  description = "Number of worker nodes"
  type        = number
  default     = 2
}

variable "enable_gpu" {
  description = "Add GPU node pool (requires GPU-capable type)"
  type        = bool
  default     = false
}

variable "gpu_node_type" {
  description = "GPU node type. Hetzner Cloud has no GPU — use cx33 (4 vCPU, 8GB) or cx43 (8 vCPU, 16GB) as placeholder."
  type        = string
  default     = "cx33"
}

variable "gpu_node_count" {
  description = "Number of GPU nodes"
  type        = number
  default     = 0
}

variable "gpu_location" {
  description = "Location for GPU pool. Use fsn1 or hel1 if nbg1 has resource_unavailable."
  type        = string
  default     = ""
}
