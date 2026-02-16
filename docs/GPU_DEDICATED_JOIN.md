# Joining Hetzner Dedicated GEX44 (GPU) to the Cluster

How to manually add a Hetzner dedicated GEX44 GPU server to your existing k3s cluster (provisioned via Terraform on Hetzner Cloud).

## Prerequisites

- Existing cluster running (from `infra/terraform`)
- GEX44 ordered via [Hetzner Robot](https://robot.hetzner.com) (FSN1 or NBG1)
- SSH access to the GEX44 (root)
- Network: GEX44 must reach the cluster API (port 6443). Use the control plane public IP from kubeconfig.

---

## 1. Get Join Credentials

From your Terraform output:

```bash
cd infra/terraform
terraform output -raw k3s_endpoint   # e.g. https://46.225.119.225:6443
terraform output -raw k3s_token     # node token
```

If `k3s_token` is not available, SSH to the control plane and read it:

```bash
# Control plane IP from: terraform output control_plane_ip
ssh root@<control-plane-ip> "cat /var/lib/rancher/k3s/server/node-token"
```

---

## 2. Prepare the GEX44

SSH to your GEX44 and run:

```bash
# Install NVIDIA drivers + container toolkit (required for GPU workloads)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
apt-get update && apt-get install -y nvidia-container-toolkit

# Configure containerd (k3s uses containerd)
nvidia-ctk runtime configure --runtime=containerd
```

---

## 3. Install k3s Agent

On the GEX44:

```bash
# Replace with your values from step 1
export K3S_URL="https://<control-plane-ip>:6443"
export K3S_TOKEN="<your-node-token>"

curl -sfL https://get.k3s.io | K3S_URL="$K3S_URL" K3S_TOKEN="$K3S_TOKEN" sh -s - agent

systemctl enable --now k3s-agent
```

---

## 4. Add GPU Labels and Taints

After the node joins, add the labels/taints so GPU jobs are scheduled here:

```bash
# From your laptop (with KUBECONFIG pointing at the cluster)
export KUBECONFIG=infra/terraform/kubeconfig.yaml

# Find the new node name (usually the hostname of the GEX44)
kubectl get nodes

# Add label and taint (replace <node-name> with actual name)
kubectl label node <node-name> quantlix.com/gpu=true
kubectl taint node <node-name> nvidia.com/gpu=true:NoSchedule
```

---

## 5. Disable Terraform GPU Pool (Optional)

If you had `enable_gpu=true` with a CPU placeholder (cpx31), you can disable it so Terraform doesn't manage GPU nodes—the GEX44 is manual:

```hcl
# terraform.tfvars
enable_gpu   = false   # We use manual GEX44 instead
# gpu_node_count = 0
```

Then `terraform apply` to remove the placeholder pool. The manually joined GEX44 stays.

---

## 6. Verify

```bash
kubectl get nodes -l quantlix.com/gpu=true
kubectl describe node <gpu-node>   # Should show nvidia.com/gpu resource
```

Deploy a GPU model and run inference—jobs with `config.gpu` will schedule on the GEX44.

**Note:** The inference container image must support GPU (CUDA base, e.g. `nvidia/cuda`). Update `INFERENCE_IMAGE` or use a GPU-enabled model image.

---

## Network Notes

- **Hetzner Cloud** and **Hetzner Dedicated** are in the same datacenters (FSN1, NBG1). The GEX44 can reach the control plane’s public IP on port 6443.
- For private networking, you’d need a VPN or Hetzner vSwitch between Cloud and Dedicated—more complex. Public IP is simplest for MVP.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Node not Ready | Check `journalctl -u k3s-agent -f`; ensure firewall allows 6443 to control plane |
| No GPU resource | Install nvidia-container-toolkit; restart k3s-agent |
| Pods not scheduling | Verify label `quantlix.com/gpu=true` and toleration in pod spec |
