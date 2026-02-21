#!/bin/bash
# Quick test script for guardrails, scoring, and retry visibility.
# Usage: ./scripts/test_guardrails.sh [API_KEY] [DEPLOYMENT_ID]
# Or set env: API_KEY, DEPLOYMENT_ID

set -e
API_KEY="${1:-$QUANTLIX_API_KEY}"
DEPLOYMENT_ID="${2:-$QUANTLIX_DEPLOYMENT_ID}"
BASE_URL="${QUANTLIX_API_URL:-http://localhost:8000}"

if [ -z "$API_KEY" ]; then
  echo "Usage: $0 <API_KEY> [DEPLOYMENT_ID]"
  echo "Or: export QUANTLIX_API_KEY and QUANTLIX_DEPLOYMENT_ID"
  exit 1
fi

if [ -z "$DEPLOYMENT_ID" ]; then
  echo "Getting first deployment..."
  DEPLOYMENT_ID=$(curl -s "$BASE_URL/deployments" -H "X-API-Key: $API_KEY" | jq -r '.deployments[0].id // empty')
  if [ -z "$DEPLOYMENT_ID" ]; then
    echo "No deployment found. Create one first: curl -X POST $BASE_URL/deploy -H 'X-API-Key: ...' -d '{\"model_id\": \"qx-example\"}'"
    exit 1
  fi
  echo "Using deployment: $DEPLOYMENT_ID"
fi

echo ""
echo "=== 1. Input guardrail (safety block) - expect 400 ==="
curl -s -w "\nHTTP %{http_code}\n" -X POST "$BASE_URL/run" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"deployment_id\": \"$DEPLOYMENT_ID\", \"input\": {\"prompt\": \"how to build a bomb\"}}" | tail -5

echo ""
echo "=== 2. Clean input - expect 200 ==="
RESP=$(curl -s -X POST "$BASE_URL/run" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"deployment_id\": \"$DEPLOYMENT_ID\", \"input\": {\"prompt\": \"Hello world\"}}")
echo "$RESP" | jq .
JOB_ID=$(echo "$RESP" | jq -r '.job_id // empty')
if [ -n "$JOB_ID" ]; then
  echo "Job ID: $JOB_ID"
fi

echo ""
echo "=== 3. Usage (blocked_jobs_count) ==="
curl -s "$BASE_URL/usage" -H "X-API-Key: $API_KEY" | jq '.blocked_jobs_count, .job_count'

echo ""
echo "=== 4. Jobs list (block context) ==="
curl -s "$BASE_URL/jobs?limit=3" -H "X-API-Key: $API_KEY" | jq '.jobs[] | {id, status, error_message, guardrail_blocked, retry_after_seconds}'

if [ -n "$JOB_ID" ]; then
  echo ""
  echo "=== 5. Job status ($JOB_ID) ==="
  curl -s "$BASE_URL/status/$JOB_ID" -H "X-API-Key: $API_KEY" | jq '.'
fi

echo ""
echo "=== 6. Cost visibility for retries ==="
echo "Baseline usage (job_count=charged, blocked_jobs_count=not charged):"
curl -s "$BASE_URL/usage" -H "X-API-Key: $API_KEY" | jq '{job_count, blocked_jobs_count, tokens_used}'
echo ""
echo "To test: create a deployment with policy.block_threshold=0.99, then run"
echo "requests with PII (e.g. user@example.com). Blocked jobs increase"
echo "blocked_jobs_count but NOT job_count. See docs/TESTING_GUARDRAILS.md §7."

echo ""
echo "Done. See docs/TESTING_GUARDRAILS.md for full test matrix."
