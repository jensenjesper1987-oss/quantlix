# Quantlix — Go-Live Guide

Step-by-step checklist for taking Quantlix to production.

---

## 1. Pre-Launch Checklist

- [ ] Domains: `quantlix.ai` (portal), `api.quantlix.ai` (API)
- [ ] SSL/TLS certificates for both domains
- [ ] Stripe account activated for live payments
- [ ] Sweego (or SMTP) configured for `support@quantlix.ai`
- [ ] Database backups configured
- [ ] Secrets stored securely (not in git)

### Verify secrets are not in git

Your `.gitignore` already excludes `.env` and `infra/terraform/terraform.tfvars`. Confirm:

```bash
# These should return nothing (files are ignored)
git check-ignore -v .env
git check-ignore -v infra/terraform/terraform.tfvars

# Ensure no secrets were ever committed
git log -p --all -S "sk_live_" -- . 2>/dev/null | head -5
git log -p --all -S "STRIPE_SECRET" -- . 2>/dev/null | head -5
```

**Production:** Use a secrets manager (Hetzner Secrets, Kubernetes Secrets, Doppler, 1Password, etc.) and inject env vars at runtime. Never bake secrets into images or config in git.

---

## 2. Environment Variables (Production)

Create or update `.env` for production. **Never commit secrets to git.**

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_PASSWORD` | Strong DB password | `openssl rand -hex 32` |
| `JWT_SECRET` | Auth signing key | `openssl rand -hex 32` |
| `APP_BASE_URL` | Public API URL for verification links | `https://api.quantlix.ai` |
| `PORTAL_BASE_URL` | Portal URL for Stripe redirects | `https://quantlix.ai` |
| `STRIPE_SECRET_KEY` | Stripe live secret key (`sk_live_...`) | From Stripe Dashboard |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret | From Stripe webhook endpoint |
| `STRIPE_PRICE_ID_STARTER` | Starter €9/mo Price ID | `price_xxx` from Stripe |
| `STRIPE_PRICE_ID_PRO` | Pro plan Price ID | `price_xxx` from Stripe |
| `SMTP_USER` | SMTP username | From Sweego dashboard |
| `SMTP_PASSWORD` | SMTP password | From Sweego dashboard |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `DEV_RETURN_VERIFICATION_LINK` | Include verification link in signup response | `false` (set to `false` in prod) |
| `USAGE_LIMIT_TOKENS_PER_MONTH` | Per-user token limit (0 = unlimited) | `0` |
| `USAGE_LIMIT_COMPUTE_SECONDS_PER_MONTH` | Per-user compute limit | `0` |

### Generate Secrets

```bash
# JWT secret
openssl rand -hex 32

# Postgres password
openssl rand -hex 24
```

---

## 3. Disable Dev Mode

Before going live:

1. **Set in `.env`:**
   ```
   DEV_RETURN_VERIFICATION_LINK=false
   ```

2. **Verify** no dev-only behavior is enabled (e.g. returning verification links in API responses).

---

## 4. Stripe Configuration

### 4.1 Webhook Endpoint

1. Go to [Stripe Dashboard → Developers → Webhooks](https://dashboard.stripe.com/webhooks)
2. Click **Add endpoint**
3. **Endpoint URL:** `https://api.quantlix.ai/billing/webhook`
4. **Events to send:**
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.deleted`
5. Click **Add endpoint**
6. Copy the **Signing secret** (`whsec_...`) and set as `STRIPE_WEBHOOK_SECRET` in `.env`

### 4.2 Business Settings

1. [Stripe Dashboard → Settings → Business](https://dashboard.stripe.com/settings/account)
2. Set **Business website** to `https://quantlix.ai`
3. Ensure account is fully activated for live payments

### 4.3 Test Webhook (Optional)

```bash
stripe listen --forward-to https://api.quantlix.ai/billing/webhook
# Use the printed webhook secret for local testing
```

---

## 5. Email (SMTP)

### Sweego

1. Create account at [sweego.io](https://app.sweego.io/signup)
2. Add domain `quantlix.ai` and configure DNS (SPF, DKIM, DMARC)
3. Generate SMTP credentials in the Sweego dashboard
4. Set `SMTP_USER` and `SMTP_PASSWORD` in `.env` (or K8s secret)

### Test

```bash
docker compose exec api python scripts/test_smtp.py
# Should output: SUCCESS: Email sent successfully
```

### Automated Email Triggers (High ROI)

Three automated emails build trust and reactivate users:

| Trigger | Subject | When |
|---------|---------|------|
| **After First Deploy** | Your Quantlix endpoint is live | When a deployment becomes ready (first time) |
| **Near Limit** | You're close to your monthly limit | Free users at 70–100% of tokens/CPU/GPU |
| **Idle Users** | Still working on your model? | 3 days inactive (no job or deployment) |

**Email 1** is sent automatically by the orchestrator worker when a deployment transitions to ready.

**Emails 2 & 3** require a daily cron job. Run:

```bash
# Daily at 09:00 UTC (adjust for your timezone)
docker compose exec api python scripts/send_trigger_emails.py
```

Or add a Kubernetes CronJob:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: trigger-emails
  namespace: quantlix
spec:
  schedule: "0 9 * * *"  # Daily at 09:00 UTC
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: trigger-emails
            image: quantlix-api:latest
            command: ["python", "scripts/send_trigger_emails.py"]
            envFrom:
            - secretRef:
                name: quantlix-secrets
          restartPolicy: OnFailure
```

---

## 6. DNS & Domains

### Records

| Type | Name | Value | Purpose |
|------|------|-------|---------|
| A / CNAME | `api` | Cluster LB IP (see below) | `api.quantlix.ai` |
| A / CNAME | `grafana` | Same LB IP as `api` | `grafana.quantlix.ai` |
| A / CNAME | `@` or `www` | Your portal/server IP | `quantlix.ai` |

**Both `api` and `grafana` use the same IP** — the cluster load balancer. Traefik routes traffic by hostname (`api.quantlix.ai` → API, `grafana.quantlix.ai` → Grafana).

**Get the LB IP** (Hetzner + kube-hetzner):
```bash
cd infra/terraform
terraform output -raw ingress_ip
```

**Important:** DNS must point to your cluster *before* Let's Encrypt can issue certificates (HTTP-01 challenge).

### SSL/TLS (cert-manager + Let's Encrypt)

For **Kubernetes** deployments, SSL is handled by cert-manager and the Let's Encrypt ClusterIssuer:

1. **Install cert-manager** (if not already present, e.g. via kube-hetzner):
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
   ```

2. **Apply base manifests** (includes `letsencrypt-issuer.yaml` and Ingress TLS):
   ```bash
   kubectl apply -k infra/kubernetes/base
   ```

3. **Deploy prod overlay** (patches Ingress hosts to `api.quantlix.ai`, `grafana.quantlix.ai`):
   ```bash
   kubectl apply -k infra/kubernetes/overlays/prod
   ```

4. **Verify certificates:**
   ```bash
   kubectl get certificates -n quantlix
   kubectl describe certificate api-quantlix-tls -n quantlix
   ```

   cert-manager will create TLS secrets (`api-quantlix-tls`, `grafana-quantlix-tls`) once DNS resolves and the HTTP-01 challenge succeeds.

5. **HTTPS redirect:** If using Traefik, set `traefik_redirect_to_https = true` in `infra/terraform/terraform.tfvars` (default) or in the module block in `main.tf`. Or configure via Traefik IngressRoute annotations.

For **Docker Compose**, use a reverse proxy (Traefik, Caddy, or nginx) in front to terminate SSL with Let's Encrypt (Certbot or built-in ACME).

---

## 7. CORS

The API allows these origins by default:

- `https://quantlix.ai`
- `https://app.quantlix.ai`
- `http://localhost:3000`, `3001`, `3002` (dev)

For **Vercel** or other custom domains, set `CORS_ORIGINS` (comma-separated):

```bash
CORS_ORIGINS=https://quantlix.vercel.app,https://www.quantlix.ai
```

Preview deployments use URLs like `https://project-git-branch-xxx.vercel.app`; add those if needed.

---

## 8. Deployment Options

### Option A: Docker Compose (VPS / Single Server)

1. **Build and run:**
   ```bash
   docker compose build
   docker compose up -d
   ```

2. **Set production env:**
   - `PORTAL_API_URL=https://api.quantlix.ai` (so portal calls correct API)
   - All production values in `.env`

3. **Reverse proxy** (nginx, Traefik, or Caddy) in front:
   - Terminate SSL
   - Route `api.quantlix.ai` → API (port 8000)
   - Route `quantlix.ai` → Portal (port 3002) or static host

4. **Remove dev mounts** (optional): In `docker-compose.yml`, remove `volumes: - .:/app` from `api` and `orchestrator` for production to use built images only.

### Option B: Kubernetes (Hetzner)

1. **Provision cluster:**
   ```bash
   cd infra/terraform
   terraform apply
   export KUBECONFIG=$(pwd)/kubeconfig.yaml
   ```

2. **Build and push images** (replace `YOUR_DOCKERHUB_USER` with your username; use `--platform linux/amd64` on Apple Silicon):
   ```bash
   docker login
   export REGISTRY=docker.io/YOUR_DOCKERHUB_USER
   docker build --platform linux/amd64 -t $REGISTRY/quantlix-api:latest -f api/Dockerfile .
   docker build --platform linux/amd64 -t $REGISTRY/quantlix-orchestrator:latest -f orchestrator/Dockerfile .
   docker build --platform linux/amd64 -t $REGISTRY/quantlix-inference:latest -f inference/Dockerfile ./inference
   docker push $REGISTRY/quantlix-api:latest
   docker push $REGISTRY/quantlix-orchestrator:latest
   docker push $REGISTRY/quantlix-inference:latest
   ```
   Update `infra/kubernetes/overlays/prod/kustomization.yaml` with your registry path (lines 12–17 and 43).

   **Alternative (ttl.sh, 24h expiry, for testing):** Use `ttl.sh/quantlix-api-quantlix:24h` etc. and push without auth.

3. **Deploy:**
   ```bash
   kubectl apply -k infra/kubernetes/overlays/prod
   ```

4. **Configure Ingress** for `api.quantlix.ai` and `quantlix.ai`

5. **Secrets:** Store env vars in Kubernetes Secrets, not in manifests

---

## 9. Portal Build (Production)

The portal needs `NEXT_PUBLIC_API_URL` at build time:

```bash
cd portal
NEXT_PUBLIC_API_URL=https://api.quantlix.ai npm run build
npm start
# Or use the Docker image with PORTAL_API_URL=https://api.quantlix.ai
```

---

## 10. Post-Launch Verification

### API

- [ ] `https://api.quantlix.ai/` returns `{"service":"quantlix","version":"0.1.0"}`
- [ ] `https://api.quantlix.ai/docs` loads Swagger UI
- [ ] Signup works and sends verification email
- [ ] Login works after verification
- [ ] Upgrade to Pro works (Stripe Checkout)
- [ ] Webhook updates plan (or use "Sync subscription" on dashboard)

### Portal

- [ ] `https://quantlix.ai` loads
- [ ] Sign up / Sign in work
- [ ] Dashboard shows account, usage, billing
- [ ] Upgrade and Manage billing redirect correctly

### Stripe

- [ ] Webhook receives events (check Stripe Dashboard → Webhooks → Logs)
- [ ] No 403 on Checkout page
- [ ] Success redirect goes to `https://quantlix.ai/dashboard?success=true`

---

## 11. Monitoring & Backups

- **Database:** Schedule PostgreSQL backups (e.g. pg_dump, managed DB backups)
- **Logs:** Ensure API and orchestrator logs are collected
- **Stripe:** Monitor [Dashboard → Developers → Logs](https://dashboard.stripe.com/logs) for errors
- **Uptime:** Consider uptime monitoring for `api.quantlix.ai` and `quantlix.ai`

---

## 12. Quick Reference

| Service | Production URL |
|---------|----------------|
| Portal | https://quantlix.ai |
| API | https://api.quantlix.ai |
| API Docs | https://api.quantlix.ai/docs |
| Stripe Webhook | https://api.quantlix.ai/billing/webhook |

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| Verification email not received | SMTP config, spam folder, Sweego DNS |
| Plan stays Free after payment | Webhook configured? Use "Sync subscription" on dashboard |
| Stripe Checkout 403 | Business website URL, account activation, Stripe support |
| CORS errors | Set `CORS_ORIGINS` with your portal URL (e.g. Vercel domain) |
| API/Orchestrator ImagePullBackOff | **Option A (no registry):** Run `./infra/kubernetes/scripts/load-images-to-nodes.sh` then `kubectl apply -k infra/kubernetes/overlays/prod-local`. Requires SSH to nodes. **Option B:** Push to Docker Hub/GHCR, update `overlays/prod/kustomization.yaml`, apply prod overlay. |

---

## Admin: Remove a User

To delete a user and all related data (api_keys, deployments, jobs, usage_records):

```bash
# From your machine (with prod DB env vars or port-forward)
python scripts/delete_user.py user@example.com

# Or inside the API pod
kubectl exec -it deploy/api -n quantlix -- python scripts/delete_user.py user@example.com
```

**Note:** Stripe customer records are not deleted. Cancel any active subscriptions in Stripe first if needed.
