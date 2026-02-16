# Quantlix — Python SDK

Thin wrapper around the Quantlix REST API for deploy, run, status, and usage.

## Installation

```bash
pip install -e .
```

## Usage

```python
from sdk.quantlix import QuantlixCloudClient

client = QuantlixCloudClient(api_key="your-api-key")

# Deploy a model
deploy = client.deploy("my-llama-7b", model_path="models/user/llama")
print(deploy.deployment_id, deploy.status)

# Run inference
run = client.run(deploy.deployment_id, {"prompt": "Hello"})
print(run.job_id, run.status)

# Check status
status = client.status(run.job_id)
print(status.status, status.output_data)

# Get usage
usage = client.usage()
print(usage.tokens_used, usage.compute_seconds)
```

## Response types

- `DeployResult` — deployment_id, status, message
- `RunResult` — job_id, status, message
- `StatusResult` — id, type, status, output_data, tokens_used, etc.
- `UsageResult` — user_id, tokens_used, compute_seconds, job_count
