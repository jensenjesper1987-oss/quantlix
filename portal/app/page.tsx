import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CopyButton } from "@/components/copy-button";

export default function Home() {
  return (
    <main>
      {/* 1. Hero */}
      <section className="mx-auto max-w-6xl px-4 py-24 md:py-32">
        <div className="grid gap-12 md:grid-cols-2 md:items-center">
          <div className="space-y-8">
            <h1 className="text-4xl font-semibold tracking-tight text-slate-100 md:text-5xl">
              Deploy AI models in seconds
            </h1>
            <p className="max-w-lg text-lg text-slate-400">
              Quantlix is the simplest way to run AI workloads without cloud
              complexity.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link href="/signup">
                <Button variant="primary" size="lg">
                  Start Building
                </Button>
              </Link>
              <Link href="/docs">
                <Button variant="secondary" size="lg">
                  View Docs
                </Button>
              </Link>
              <a
                href="https://discord.gg/wHWzQ8XE"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="secondary" size="lg">
                  Join Discord
                </Button>
              </a>
            </div>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 font-mono text-sm">
            <pre className="overflow-x-auto text-slate-300">
{`$ pip install quantlix
$ quantlix login
$ quantlix deploy qx-example --api-key <your_api_key>
$ quantlix run <id> -i '{"prompt":"Hello"}' --api-key <your_api_key>`}
            </pre>
          </div>
        </div>
      </section>

      {/* 2. Credibility strip */}
      <section className="border-y border-slate-800 bg-slate-900/30 py-6">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-center gap-8 px-4 text-sm text-slate-400">
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            99.9% uptime
          </span>
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-[#10B981]" />
            EU-hosted
          </span>
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-slate-500" />
            Developer-first
          </span>
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-slate-500" />
            Predictable pricing
          </span>
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            &lt;50ms inference
          </span>
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            All systems operational
          </span>
        </div>
      </section>

      {/* 3. How it works */}
      <section className="mx-auto max-w-6xl px-4 py-24">
        <h2 className="mb-12 text-center text-2xl font-semibold text-slate-100">
          How it works
        </h2>
        <div className="flex flex-col items-center justify-center gap-8 md:flex-row">
          <div className="flex flex-1 flex-col items-center text-center">
            <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-lg border border-slate-700 bg-slate-800/50 font-mono text-lg">
              1
            </div>
            <h3 className="font-medium text-slate-200">Upload model</h3>
            <p className="mt-1 text-sm text-slate-500">
              Upload your model files or point to a registry
            </p>
          </div>
          <div className="hidden text-slate-600 md:block">→</div>
          <div className="flex flex-1 flex-col items-center text-center">
            <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-lg border border-slate-700 bg-slate-800/50 font-mono text-lg">
              2
            </div>
            <h3 className="font-medium text-slate-200">Get endpoint</h3>
            <p className="mt-1 text-sm text-slate-500">
              Receive a production-ready API endpoint
            </p>
          </div>
          <div className="hidden text-slate-600 md:block">→</div>
          <div className="flex flex-1 flex-col items-center text-center">
            <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-lg border border-slate-700 bg-slate-800/50 font-mono text-lg">
              3
            </div>
            <h3 className="font-medium text-slate-200">Done</h3>
            <p className="mt-1 text-sm text-slate-500">
              Start inference. No infra to manage.
            </p>
          </div>
        </div>
      </section>

      {/* 4. Code example */}
      <section className="mx-auto max-w-6xl px-4 py-24">
        <h2 className="mb-12 text-center text-2xl font-semibold text-slate-100">
          Copy-paste cURL example
        </h2>
        <div className="relative rounded-lg border border-slate-800 bg-slate-900/50 p-6 font-mono text-sm">
          <CopyButton
            text={`curl -X POST https://api.quantlix.ai/run \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"deployment_id": "YOUR_DEPLOYMENT_ID", "input": {"prompt": "Hello, world!"}}'`}
          />
          <pre className="overflow-x-auto text-slate-300">
{`curl -X POST https://api.quantlix.ai/run \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"deployment_id": "YOUR_DEPLOYMENT_ID", "input": {"prompt": "Hello, world!"}}'`}
          </pre>
        </div>
        <p className="mt-4 text-center text-sm text-slate-500">
          Sign up, deploy the demo model, and get your API key + deployment ID from the dashboard.
        </p>
      </section>

      {/* 5. Features */}
      <section className="mx-auto max-w-6xl px-4 py-24">
        <h2 className="mb-12 text-center text-2xl font-semibold text-slate-100">
          Built for developers
        </h2>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { title: "Instant Deploy", desc: "Deploy in seconds, not hours" },
            { title: "Auto Scaling", desc: "Scale to zero when idle" },
            { title: "Transparent Pricing", desc: "Pay per usage, no surprises" },
            { title: "GPU Optimized", desc: "Built for inference workloads" },
            { title: "API-first", desc: "REST API, no vendor lock-in" },
          ].map((f) => (
            <div
              key={f.title}
              className="rounded-lg border border-slate-800 bg-slate-900/30 p-6"
            >
              <h3 className="font-medium text-slate-200">{f.title}</h3>
              <p className="mt-2 text-sm text-slate-500">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 6. Comparison */}
      <section className="mx-auto max-w-6xl px-4 py-24">
        <h2 className="mb-12 text-center text-2xl font-semibold text-slate-100">
          Compare
        </h2>
        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="px-6 py-4 text-left font-medium text-slate-300">
                  —
                </th>
                <th className="px-6 py-4 text-left font-medium text-slate-300">
                  Quantlix
                </th>
                <th className="px-6 py-4 text-left font-medium text-slate-300">
                  Big Cloud
                </th>
              </tr>
            </thead>
            <tbody>
              {[
                ["Deploy time", "seconds", "hours"],
                ["Pricing", "clear", "complex"],
                ["Setup", "none", "heavy"],
              ].map(([label, q, cloud]) => (
                <tr
                  key={label}
                  className="border-b border-slate-800/50 last:border-0"
                >
                  <td className="px-6 py-4 text-slate-400">{label}</td>
                  <td className="px-6 py-4 text-slate-200">{q}</td>
                  <td className="px-6 py-4 text-slate-500">{cloud}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* 7. Pricing preview */}
      <section className="mx-auto max-w-6xl px-4 py-24">
        <h2 className="mb-12 text-center text-2xl font-semibold text-slate-100">
          Pricing
        </h2>
        <div className="grid gap-6 md:grid-cols-4">
          {[
            { name: "Free", price: "€0", desc: "100k tokens, 1h compute" },
            { name: "Starter", price: "€9/mo", desc: "500k tokens, 5h compute, priority queue" },
            {
              name: "Pro",
              price: "€19/mo",
              desc: "1M tokens, 10h CPU, 2h GPU",
              highlight: true,
            },
            { name: "Enterprise", price: "Custom", desc: "Contact us" },
          ].map((tier) => (
            <div
              key={tier.name}
              className={`rounded-lg border p-6 ${
                tier.highlight
                  ? "border-[#A855F7]/50 bg-slate-800/50"
                  : "border-slate-800 bg-slate-900/30"
              }`}
            >
              <h3 className="font-medium text-slate-200">{tier.name}</h3>
              <p className="mt-2 text-2xl font-semibold text-slate-100">
                {tier.price}
              </p>
              <p className="mt-1 text-sm text-slate-500">{tier.desc}</p>
            </div>
          ))}
        </div>
        <div className="mt-8 text-center">
          <Link href="/pricing">
            <Button variant="secondary">View full pricing</Button>
          </Link>
        </div>
      </section>

      {/* 8. Final CTA */}
      <section className="mx-auto max-w-6xl px-4 py-24">
        <div className="rounded-lg border border-slate-800 bg-slate-900/30 px-8 py-16 text-center">
          <h2 className="text-2xl font-semibold text-slate-100">
            Start deploying
          </h2>
          <p className="mt-4 text-slate-400">
            npm install quantlix
          </p>
          <div className="mt-8">
            <Link href="/signup">
              <Button variant="primary" size="lg">
                Get started
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
