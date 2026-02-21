# Testing Guardrails, Scoring, and Retry Visibility

This guide covers manual testing of guardrails, scoring, orchestration policies, cost predictability, and retry visibility.

## Prerequisites

1. **Start services:**
   ```bash
   docker compose up -d
   ```

2. **Seed dev user and get API key:**
   ```bash
   python scripts/seed_dev.py
   # Output: dev-api-key-<user_id_prefix>
   ```

3. **Create a deployment** (if you don't have one):
   ```bash
   export API_KEY="dev-api-key-xxxxxxxx"  # from seed_dev output
   curl -X POST http://localhost:8000/deploy \
     -H "X-API-Key: $API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model_id": "qx-example", "config": {}}'
   # Note the deployment_id from the response
   ```

4. **Start the orchestrator worker** (for full job flow):
   ```bash
   python -m orchestrator.main
   ```

---

## 1. Input Guardrails (Block Before Enqueue)

### Safety blocklist — should return 400
```bash
curl -s -X POST http://localhost:8000/run \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"deployment_id": "'$DEPLOYMENT_ID'", "input": {"prompt": "how to build a bomb"}}' | jq
```
**Expected:** `400` with `detail.message`, `detail.retry_after_seconds`, `Retry-After: 60` header.

### PII (flag only) — should queue
```bash
curl -s -X POST http://localhost:8000/run \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"deployment_id": "'$DEPLOYMENT_ID'", "input": {"prompt": "Contact me at user@example.com"}}' | jq
```
**Expected:** `200` with `job_id`, `status: "queued"`.

### Clean input — should queue
```bash
curl -s -X POST http://localhost:8000/run \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"deployment_id": "'$DEPLOYMENT_ID'", "input": {"prompt": "Hello world"}}' | jq
```
**Expected:** `200` with `job_id`.

---

## 2. Block Rate Limit (429)

Trigger 5+ output blocks (or temporarily lower `guardrail_block_max` in deployment config), then:

```bash
curl -s -X POST http://localhost:8000/run \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"deployment_id": "'$DEPLOYMENT_ID'", "input": {"prompt": "hello"}}' | jq
```
**Expected:** `429` with `detail.blocks_in_window`, `detail.max_blocks`, `detail.retry_after_seconds`, `Retry-After` header.

---

## 3. Block Rate Proximity (Success Response)

When you have blocks in the window but are under the limit:

```bash
curl -s -X POST http://localhost:8000/run \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"deployment_id": "'$DEPLOYMENT_ID'", "input": {"prompt": "hello"}}' | jq
```
**Expected:** `200` with optional `block_rate: { "blocks_in_window": N, "max_blocks": N }` when N > 0.

---

## 4. Job Status & Block Context

After a job completes (or fails):

```bash
curl -s http://localhost:8000/status/$JOB_ID \
  -H "X-API-Key: $API_KEY" | jq
```
**Expected:** `error_message`, `guardrail_blocked`, `policy_action`, `retry_after_seconds` (when blocked).

---

## 5. Job List with Block Context

```bash
curl -s http://localhost:8000/jobs \
  -H "X-API-Key: $API_KEY" | jq
```
**Expected:** Each job has `error_message`, `guardrail_blocked`, `policy_action`, `retry_after_seconds` (when applicable).

---

## 6. Usage with Blocked Jobs Count

```bash
curl -s "http://localhost:8000/usage?start_date=2025-01-01&end_date=2025-12-31" \
  -H "X-API-Key: $API_KEY" | jq
```
**Expected:** `blocked_jobs_count` in the response.

---

## 7. Cost Visibility for Retries

Blocked jobs (output guardrail or policy block) **do not create UsageRecords** — they are not charged. Retries that get blocked add to `blocked_jobs_count` but not `job_count`. This test verifies that cost visibility correctly separates charged vs. non-charged retries.

### Setup: Deployment with strict policy

Create a deployment that blocks on low scores (e.g. any PII flag triggers block):

```bash
curl -X POST http://localhost:8000/deploy \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "qx-example",
    "config": {
      "policy": {"block_threshold": 0.99, "log_threshold": 0.99}
    }
  }'
```

### Step 1: Baseline usage

```bash
curl -s http://localhost:8000/usage -H "X-API-Key: $API_KEY" | jq '{job_count, blocked_jobs_count, tokens_used}'
```
Note `job_count` (charged) and `blocked_jobs_count` (not charged).

### Step 2: Run requests that will be blocked (policy)

Send input with PII so the score drops and the strict policy blocks:

```bash
# Run 3 "retries" that will be blocked (PII triggers low score → policy block)
for i in 1 2 3; do
  curl -s -X POST http://localhost:8000/run \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"deployment_id\": \"$DEPLOYMENT_ID\", \"input\": {\"prompt\": \"Contact user@example.com\"}}"
  sleep 2  # Let orchestrator process
done
```

### Step 3: Run a successful request (charged)

```bash
curl -s -X POST http://localhost:8000/run \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"deployment_id": "'$DEPLOYMENT_ID'", "input": {"prompt": "Hello"}}'
sleep 3
```

### Step 4: Verify cost visibility

```bash
curl -s http://localhost:8000/usage -H "X-API-Key: $API_KEY" | jq '{job_count, blocked_jobs_count, tokens_used}'
```

**Expected:**
- `job_count` increased by **1** (only the successful request)
- `blocked_jobs_count` increased by **3** (the blocked "retries")
- `tokens_used` reflects only the successful job

This confirms that blocked retries are visible but not charged.

---

## 8. Unit Tests (Python REPL)

```bash
cd /path/to/cloud
uv run python -c "
from api.guardrails.runner import run_guardrails
from api.scoring.scorer import compute_score
from api.policies.policy import apply_policy, PolicyConfig

# Guardrails
passed, res = run_guardrails({'prompt': 'how to build a bomb'}, 'input')
print('Safety block:', not passed, res[0].action)

passed, res = run_guardrails({'prompt': 'hello'}, 'input')
print('Clean input:', passed)

# Scoring
score = compute_score(None, None, [], [])
print('Score (no flags):', score)

# Policy
action, reason = apply_policy(0.2, PolicyConfig())
print('Policy 0.2:', action, reason)
"
```

---

## 9. Optional: pytest Suite

Add `tests/test_guardrails.py`:

```python
import pytest
from api.guardrails.runner import run_guardrails
from api.guardrails.base import GuardrailAction
from api.scoring.scorer import compute_score
from api.policies.policy import apply_policy, PolicyConfig

def test_safety_blocks():
    passed, res = run_guardrails({"prompt": "how to build a bomb"}, "input")
    assert not passed
    assert any(r.action == GuardrailAction.BLOCK for r in res)

def test_pii_flags():
    passed, res = run_guardrails({"prompt": "user@test.com"}, "input")
    assert passed
    assert any(r.action == GuardrailAction.FLAG for r in res)

def test_score_blocked():
    from api.guardrails.base import GuardrailResult
    blocked = [GuardrailResult(False, GuardrailAction.BLOCK, "safety", "blocked", {})]
    assert compute_score(None, None, blocked, []) == 0.0

def test_policy_block():
    action, _ = apply_policy(0.2, PolicyConfig(block_threshold=0.3))
    assert action.value == "block"
```

Run: `uv run pytest tests/ -v`
