# Quantlix — JavaScript/TypeScript SDK

Thin wrapper around the Quantlix REST API for deploy, run, status, and usage.

## Installation

```bash
npm install @quantlix/sdk
# or
pnpm add @quantlix/sdk
# or
yarn add @quantlix/sdk
```

For local development from this repo:

```bash
cd sdk/js && npm install && npm run build
```

## Usage

### Node.js / TypeScript

```typescript
import { QuantlixCloudClient } from "@quantlix/sdk";

const client = new QuantlixCloudClient(process.env.QUANTLIX_API_KEY!);

// Deploy a model
const deploy = await client.deploy("my-llama-7b", {
  modelPath: "models/user/llama",
  config: { replicas: 1 },
});
console.log(deploy.deployment_id, deploy.status);

// Run inference
const run = await client.run(deploy.deployment_id, { prompt: "Hello" });
console.log(run.job_id, run.status);

// Check status
const status = await client.status(run.job_id);
console.log(status.status, status.output_data);

// Get usage
const usage = await client.usage({
  startDate: "2025-01-01",
  endDate: "2025-02-14",
});
console.log(usage.tokens_used, usage.compute_seconds);
```

### Signup / Login

```typescript
import { QuantlixCloudClient } from "@quantlix/sdk";

// Sign up (no API key needed)
const { api_key, user_id } = await QuantlixCloudClient.signup(
  "you@example.com",
  "password123"
);

// Log in
const { api_key } = await QuantlixCloudClient.login(
  "you@example.com",
  "password123"
);

// Use the API key
const client = new QuantlixCloudClient(api_key);
```

### Browser

```html
<script type="module">
  import { QuantlixCloudClient } from "https://cdn.jsdelivr.net/npm/@quantlix/sdk/dist/index.mjs";
  const client = new QuantlixCloudClient("your-api-key");
  const deploy = await client.deploy("my-model");
  console.log(deploy);
</script>
```

## API

- `QuantlixCloudClient(apiKey, baseUrl?)` — Create client
- `client.deploy(modelId, { modelPath?, config? })` — Deploy model
- `client.run(deploymentId, input)` — Run inference
- `client.status(resourceId)` — Get deployment or job status
- `client.usage({ startDate?, endDate? })` — Get usage stats
- `QuantlixCloudClient.signup(email, password, baseUrl?)` — Create account
- `QuantlixCloudClient.login(email, password, baseUrl?)` — Log in

## Types

- `DeployResult` — deployment_id, status, message
- `RunResult` — job_id, status, message
- `StatusResult` — id, type, status, output_data, tokens_used, etc.
- `UsageResult` — user_id, tokens_used, compute_seconds, job_count
- `AuthResult` — api_key, user_id
