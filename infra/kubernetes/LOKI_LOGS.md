# Loki + Promtail — Error Logs in Grafana

Logs from the Quantlix API and orchestrator are collected by Promtail and stored in Loki. View them in Grafana at **Quantlix → Quantlix Error Logs**.

## Components

- **Loki** — Log storage (Deployment + Service)
- **Promtail** — DaemonSet that ships pod logs from the `quantlix` namespace to Loki
- **Grafana** — Loki datasource + Error Logs dashboard (auto-provisioned)

## Deploy

```bash
kubectl apply -k infra/kubernetes/overlays/dev   # or prod
```

The Error Logs dashboard appears under **Dashboards → Quantlix** after Grafana starts.

## Dashboard panels

1. **Error logs** — All logs matching `error`, `exception`, `failed`, `traceback` (case-insensitive)
2. **API errors** — Same filter, API pods only
3. **Orchestrator errors** — Same filter, orchestrator pods only
4. **All logs** — Unfiltered; use the search box to filter

## Log path (Promtail)

Promtail reads from `/var/log/pods` on each node. If logs are empty:

- Ensure nodes use containerd/docker with logs at `/var/log/pods`
- On some setups the path may differ; check Promtail logs: `kubectl logs -n quantlix -l app=promtail`

## Portal logs

The portal (www.quantlix.ai) typically runs outside the cluster (e.g. Vercel). Its logs are not collected here. Use your hosting provider’s log viewer for portal errors.
