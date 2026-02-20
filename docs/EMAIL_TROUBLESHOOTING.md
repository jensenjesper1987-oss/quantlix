# Email (Sweego) Troubleshooting

## Quick checks

### 1. Verify secrets in Kubernetes

```bash
kubectl get secret api -n quantlix -o jsonpath='{.data}' | jq 'keys'
```

Ensure `sweego-api-key` exists. If not:

```bash
kubectl create secret generic api -n quantlix \
  --from-literal=sweego-api-key=YOUR_SWEEGO_API_KEY \
  --from-literal=email-enabled=true \
  --dry-run=client -o yaml | kubectl apply -f -
# Or patch: kubectl patch secret api -n quantlix -p '{"stringData":{"sweego-api-key":"..."}}'
```

### 2. Test email from inside the API pod

```bash
kubectl exec deploy/api -n quantlix -- python scripts/test_smtp.py your@email.com
```

This uses the same config as the running API. If it fails, you'll see the Sweego error.

### 3. Check API logs for email errors

```bash
kubectl logs deploy/api -n quantlix --tail=100 | grep -i -E "email|sweego|verification"
```

After signup, look for "Signup: verification email failed" or "Sweego API error".

### 4. Sweego auth type

Sweego uses `Api-Key` by default. If your API key expects a different header:

```bash
# In K8s secret, add:
sweego-auth-type: api_key   # or api_token, bearer
```

Set via env in the deployment or patch the api secret:

```bash
kubectl patch secret api -n quantlix -p '{"stringData":{"sweego-auth-type":"api_key"}}'
```

### 5. Domain verification

Sweego requires a **verified sending domain**. If `support@quantlix.ai` is not verified in your Sweego dashboard, emails will fail.

- Log in to [Sweego](https://app.sweego.io)
- Check domain verification status
- Ensure SPF/DKIM records are in place

### 6. Dev fallback: return verification link in signup response

For testing when email is unreliable:

```bash
# Set in API env:
DEV_RETURN_VERIFICATION_LINK=true
```

The signup response will include `verification_link` so you can manually verify the user.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Email not configured` | SWEEGO_API_KEY not set | Add sweego-api-key to api secret |
| `401 Unauthorized` | Wrong API key or auth type | Check key, try `api_key` or `api_token` |
| `422` / `domain not verified` | Sending domain not verified in Sweego | Verify quantlix.ai in Sweego dashboard |
| `Sweego API error 4xx` | Check logs for body | Inspect kubectl logs for full response |
