output "kubeconfig" {
  description = "Kubernetes config for cluster access. Run: terraform output -raw kubeconfig > kubeconfig.yaml"
  value       = module.kube_hetzner.kubeconfig
  sensitive   = true
}

output "cluster_name" {
  description = "Cluster name"
  value       = var.cluster_name
}

output "k3s_endpoint" {
  description = "K3s API endpoint for joining nodes (e.g. https://ip:6443). Use with GEX44 manual join."
  value       = module.kube_hetzner.k3s_endpoint
}

output "k3s_token" {
  description = "K3s node token for joining agents. Use with GEX44 manual join. terraform output -raw k3s_token"
  value       = module.kube_hetzner.k3s_token
  sensitive   = true
}

output "control_plane_ip" {
  description = "First control plane public IP (for SSH to get token if k3s_token output unavailable)"
  value       = module.kube_hetzner.control_planes_public_ipv4[0]
}
