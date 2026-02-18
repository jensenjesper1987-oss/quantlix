# Grafana Business Metrics Dashboard

This dashboard shows **users**, **usage**, and **tiers** for Quantlix. It requires:

1. **Prometheus** scraping the API at `/metrics`
2. **Grafana** with Prometheus as a datasource

## Metrics Exposed by the API

The API exposes these custom Prometheus metrics (updated every 60 seconds):

| Metric | Description |
|--------|-------------|
| `quantlix_users_total` | Total registered users |
| `quantlix_users_verified` | Users with verified email |
| `quantlix_users_by_plan{plan}` | Users per tier (free, starter, pro) |
| `quantlix_usage_tokens_total` | Total tokens used this month |
| `quantlix_usage_compute_seconds_total` | CPU compute seconds this month |
| `quantlix_usage_gpu_seconds_total` | GPU seconds this month |
| `quantlix_usage_jobs_total` | Inference jobs this month |

## Import into Grafana

1. Open **Grafana** → https://grafana.quantlix.ai/
2. Go to **Dashboards** → **Import**
3. Upload `infra/grafana/dashboards/quantlix-business-metrics.json` or paste its contents
4. Select your **Prometheus** datasource (the one scraping the API)
5. Click **Import**

## Prometheus Configuration

Ensure Prometheus scrapes the API:

```yaml
scrape_configs:
  - job_name: api
    static_configs:
      - targets: ["api:8000"]  # or https://api.quantlix.ai for prod
    metrics_path: /metrics
    scrape_interval: 15s
```

For production (Kubernetes), the API service is typically `api.quantlix.svc.cluster.local:8000` or the internal URL.

## Troubleshooting

- **No data**: Check that Prometheus is scraping the API. Visit `https://api.quantlix.ai/metrics` and confirm you see `quantlix_users_total` and similar metrics.
- **Datasource not found**: When importing, select your Prometheus datasource. If you don't have one, add it: **Connections** → **Data sources** → **Add data source** → **Prometheus** → set URL to your Prometheus instance.
