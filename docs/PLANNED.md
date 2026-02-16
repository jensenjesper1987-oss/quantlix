# Planned Features

---

## GPU Deployment

**Status:** Backend implemented. Infra (GPU node pool) not yet wired.

**Implemented:**
- CLI `--gpu` flag (`quantlix deploy --gpu`)
- API: `config.gpu` on deploy, usage tracking (gpu_seconds, gpu_limit, gpu_seconds_overage)
- Orchestrator: records gpu_seconds for GPU deployments
- Limits: Free = 0 GPU, Pro = 2h/month included; overage allowed and tracked for billing
- Dashboard: shows GPU usage and overage

**Implemented:**
- GPU node pool in Terraform: `enable_gpu`, `gpu_node_type`, `gpu_node_count` — adds `workers-gpu` pool with labels/taints
- Orchestrator schedules GPU jobs to GPU pool via nodeSelector + toleration

**Note:** Hetzner Cloud has no GPU. Use `cpx31` (or larger) as placeholder. For real GPU: Hetzner dedicated GEX44 or another cloud.
- Stripe metered billing for GPU overage (€0.50/hr)

**Pricing model:** Pro includes 2h GPU/month; extra hours at €0.50/hr. Keeps €19 Pro profitable.

**Reference:** Hetzner GEX44 (RTX 4000 Ada, 20GB) ~€184–205/month (~€0.30/hr cost).
