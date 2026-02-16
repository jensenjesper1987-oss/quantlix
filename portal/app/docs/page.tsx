import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CopyButton } from "@/components/copy-button";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.quantlix.ai";

export default function DocsPage() {
  return (
    <main className="mx-auto max-w-4xl px-4 py-16">
      <h1 className="text-3xl font-semibold text-slate-100">
        Documentation
      </h1>
      <p className="mt-4 text-slate-400">
        Get from zero to inference in under a minute.
      </p>

      <div className="mt-12 space-y-10">
        <section className="rounded-lg border-2 border-[#A855F7]/40 bg-slate-900/50 p-6">
          <h2 className="font-medium text-slate-200">1. One-click demo deploy</h2>
          <p className="mt-2 text-sm text-slate-500">
            Go to your dashboard and click &quot;Deploy demo (one click)&quot;. The preloaded DistilGPT2 model will be ready in seconds.
          </p>
          <Link href="/dashboard" className="mt-4 inline-block">
            <Button variant="primary" size="sm">
              Open dashboard
            </Button>
          </Link>
        </section>

        <section className="rounded-lg border border-slate-800 bg-slate-900/30 p-6">
          <h2 className="font-medium text-slate-200">2. Copy-paste cURL</h2>
          <p className="mt-2 text-sm text-slate-500">
            Replace YOUR_API_KEY and YOUR_DEPLOYMENT_ID with values from your dashboard.
          </p>
          <div className="relative mt-4 rounded border border-slate-700 bg-slate-800/50 p-4 font-mono text-sm text-slate-300">
            <CopyButton
              text={`curl -X POST ${API_URL}/run \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"deployment_id": "YOUR_DEPLOYMENT_ID", "input": {"prompt": "Hello, world!"}}'`}
            />
            <pre className="overflow-x-auto whitespace-pre-wrap">
{`curl -X POST ${API_URL}/run \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"deployment_id": "YOUR_DEPLOYMENT_ID", "input": {"prompt": "Hello, world!"}}'`}
            </pre>
          </div>
        </section>

        <section className="rounded-lg border border-slate-800 bg-slate-900/30 p-6">
          <h2 className="font-medium text-slate-200">3. CLI quickstart</h2>
          <p className="mt-2 text-sm text-slate-500">
            Install, authenticate, deploy the demo model, and run inference.
          </p>
          <div className="relative mt-4 rounded border border-slate-700 bg-slate-800/50 p-4 font-mono text-sm text-slate-300">
            <CopyButton
              text={`pip install quantlix
quantlix login
quantlix deploy qx-example
quantlix run <deployment_id> -i '{"prompt": "Hello!"}'`}
            />
            <pre className="overflow-x-auto whitespace-pre-wrap">
{`pip install quantlix
quantlix login
quantlix deploy qx-example
quantlix run <deployment_id> -i '{"prompt": "Hello!"}'`}
            </pre>
          </div>
        </section>

        <section className="rounded-lg border border-slate-800 bg-slate-900/30 p-6">
          <h2 className="font-medium text-slate-200">API reference</h2>
          <p className="mt-2 text-sm text-slate-500">
            Full REST API documentation with OpenAPI spec.
          </p>
          <a
            href={`${API_URL}/docs`}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-block"
          >
            <Button variant="secondary" size="sm">
              Open API docs
            </Button>
          </a>
        </section>
      </div>
    </main>
  );
}
