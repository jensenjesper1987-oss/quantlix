#!/bin/bash
# Test cost visibility for retries: blocked jobs don't charge, but are visible.
# Requires: API running, orchestrator worker running, deployment with strict policy.
#
# Usage: ./scripts/test_cost_visibility_retries.sh [API_KEY] [DEPLOYMENT_ID]
# Or: export QUANTLIX_API_KEY, QUANTLIX_DEPLOYMENT_ID
# For slow prod (K8s): export TEST_WAIT_MAX=120  # seconds to wait for jobs

set -e
API_KEY="${1:-$QUANTLIX_API_KEY}"
DEPLOYMENT_ID="${2:-$QUANTLIX_DEPLOYMENT_ID}"
BASE_URL="${QUANTLIX_API_URL:-http://localhost:8000}"

if [ -z "$API_KEY" ]; then
  echo "Usage: $0 <API_KEY> [DEPLOYMENT_ID]"
  echo "Or: export QUANTLIX_API_KEY and QUANTLIX_DEPLOYMENT_ID"
  exit 1
fi

echo "=== Cost visibility for retries ==="
echo "Blocked jobs (output guardrail or policy) are NOT charged."
echo "They appear in blocked_jobs_count but not job_count."
echo ""

# Create deployment with strict policy if needed
if [ -z "$DEPLOYMENT_ID" ]; then
  echo "Creating deployment with strict policy (block_threshold=0.99)..."
  echo "  API: $BASE_URL"
  DEPLOY_RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/deploy" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model_id": "qx-example", "config": {"policy": {"block_threshold": 0.99, "log_threshold": 0.99}}}')
  HTTP_BODY=$(echo "$DEPLOY_RESP" | sed '$d')
  HTTP_CODE=$(echo "$DEPLOY_RESP" | tail -1)
  if [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "201" ]; then
    echo "  Deploy failed (HTTP $HTTP_CODE): $HTTP_BODY" | head -c 200
    echo ""
  fi
  DEPLOYMENT_ID=$(echo "$HTTP_BODY" | jq -r '.deployment_id // empty' 2>/dev/null)
  if [ -z "$DEPLOYMENT_ID" ]; then
    echo "  No deployment_id in response, trying deployments list..."
    DEPLOYMENT_ID=$(curl -s "$BASE_URL/deployments" -H "X-API-Key: $API_KEY" | jq -r '.deployments[0].id // empty' 2>/dev/null)
  fi
  if [ -z "$DEPLOYMENT_ID" ]; then
    echo "Could not get deployment. Set QUANTLIX_API_URL if testing remote (e.g. https://api.quantlix.ai)"
    echo "Or pass deployment ID: $0 \$API_KEY <deployment_id>"
    exit 1
  fi
  echo "Using deployment: $DEPLOYMENT_ID"
  echo "  Verifying policy config in deployment..."
  DEPLOY_STATUS=$(curl -s "$BASE_URL/status/$DEPLOYMENT_ID" -H "X-API-Key: $API_KEY")
  DEPLOY_CFG=$(echo "$DEPLOY_STATUS" | jq -r '.config.policy // "missing"')
  echo "  deployment.config.policy: $DEPLOY_CFG"
  sleep 5  # Let deployment become ready
fi

echo ""
echo "--- Step 1: Baseline usage ---"
BEFORE=$(curl -s "$BASE_URL/usage" -H "X-API-Key: $API_KEY")
echo "$BEFORE" | jq '{job_count, blocked_jobs_count, tokens_used}'
JOB_COUNT_BEFORE=$(echo "$BEFORE" | jq -r '.job_count')
BLOCKED_BEFORE=$(echo "$BEFORE" | jq -r '.blocked_jobs_count')

echo ""
echo "--- Step 2: Run 2 requests that will be BLOCKED (PII → low score → policy block) ---"
JOB1_RESP=""
for i in 1 2; do
  RESP=$(curl -s -X POST "$BASE_URL/run" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"deployment_id\": \"$DEPLOYMENT_ID\", \"input\": {\"prompt\": \"Contact user@example.com\"}}")
  echo "$RESP" | jq -c '.'
  [ -z "$JOB1_RESP" ] && JOB1_RESP="$RESP"
  echo "  (waiting 30s for worker...)"
  sleep 30
done

echo ""
echo "--- Step 3: Run 1 request that will SUCCEED (no PII) ---"
curl -s -X POST "$BASE_URL/run" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"deployment_id\": \"$DEPLOYMENT_ID\", \"input\": {\"prompt\": \"Hello world\"}}" | jq -c '.'
echo "  (waiting 30s for worker...)"
sleep 30

echo ""
echo "--- Step 3b: Wait for first job to complete (prod K8s can be slow) ---"
JOB1_ID=$(echo "$JOB1_RESP" | jq -r '.job_id // empty')
WAIT_MAX=${TEST_WAIT_MAX:-90}
WAITED=0
if [ -n "$JOB1_ID" ]; then
  while [ "$WAITED" -lt "$WAIT_MAX" ]; do
    JOB1_STATUS=$(curl -s "$BASE_URL/status/$JOB1_ID" -H "X-API-Key: $API_KEY")
    STATUS=$(echo "$JOB1_STATUS" | jq -r '.status')
    if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
      echo "Job $JOB1_ID finished ($STATUS) after ${WAITED}s"
      break
    fi
    echo "  Job $JOB1_ID: $STATUS (waited ${WAITED}s, polling every 10s...)"
    sleep 10
    WAITED=$((WAITED + 10))
  done
  if [ "$WAITED" -ge "$WAIT_MAX" ]; then
    echo "  WARNING: Job did not complete within ${WAIT_MAX}s"
  fi
fi

echo ""
echo "--- Step 3c: Diagnostic — job status ---"
if [ -n "$JOB1_ID" ]; then
  JOB1_STATUS=$(curl -s "$BASE_URL/status/$JOB1_ID" -H "X-API-Key: $API_KEY")
  echo "Job $JOB1_ID: $(echo "$JOB1_STATUS" | jq -c '{status, error_message, guardrail_blocked, policy_action}')"
  if [ "$(echo "$JOB1_STATUS" | jq -r '.status')" = "queued" ]; then
    echo "  -> Job still queued: orchestrator may not be consuming Redis queue."
  fi
fi

echo ""
echo "--- Step 4: Usage after (cost visibility) ---"
AFTER=$(curl -s "$BASE_URL/usage" -H "X-API-Key: $API_KEY")
echo "$AFTER" | jq '{job_count, blocked_jobs_count, tokens_used}'
JOB_COUNT_AFTER=$(echo "$AFTER" | jq -r '.job_count')
BLOCKED_AFTER=$(echo "$AFTER" | jq -r '.blocked_jobs_count')

echo ""
echo "--- Verification ---"
echo "job_count (charged):      $JOB_COUNT_BEFORE -> $JOB_COUNT_AFTER (expected +1)"
echo "blocked_jobs_count:       $BLOCKED_BEFORE -> $BLOCKED_AFTER (expected +2)"
echo ""
if [ "$((JOB_COUNT_AFTER - JOB_COUNT_BEFORE))" -eq 1 ] && [ "$((BLOCKED_AFTER - BLOCKED_BEFORE))" -ge 1 ]; then
  echo "PASS: Blocked retries visible but not charged."
else
  echo "FAIL: See diagnostic above. Common causes:"
  echo "  - Jobs still queued: orchestrator not consuming (check Redis URL, kubectl logs deploy/orchestrator -n quantlix)"
  echo "  - Jobs completed but policy not blocking: deployment config may not have policy.block_threshold=0.99"
  echo "  - To debug: scale to 1 replica and check logs for 'Guardrails:' and 'Policy:' lines:"
  echo "    kubectl scale deployment orchestrator -n quantlix --replicas=1"
  echo "    ./scripts/test_cost_visibility_retries.sh"
  echo "    kubectl logs deploy/orchestrator -n quantlix --tail=50"
  echo "    kubectl scale deployment orchestrator -n quantlix --replicas=2  # restore"
fi
