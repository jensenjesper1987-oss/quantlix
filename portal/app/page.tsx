import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CopyButton } from "@/components/copy-button";
import { CostCalculator } from "@/components/cost-calculator";
import { LiveDemo } from "@/components/live-demo";

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
            <div className="flex flex-wrap items-center gap-4">
              <Link href="/signup">
                <Button variant="primary" size="lg">
                  Start Building
                </Button>
              </Link>
              <a href="#live-demo">
                <Button variant="outline" size="lg">
                  Try demo (no signup)
                </Button>
              </a>
              <Link href="/docs">
                <Button variant="secondary" size="lg">
                  View Docs
                </Button>
              </Link>
              <a
                href="https://discord.gg/wHWzQ8XE"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-slate-200 underline underline-offset-4 transition-colors"
              >
                @Welcome to join Discord
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

      {/* 2b. Social proof */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="mb-8 text-center text-2xl font-semibold text-slate-100">
          Deployed models powered by Quantlix
        </h2>
        <div className="flex flex-wrap items-center justify-center gap-8 text-slate-400">
          <a
            href="https://github.com/jensenjesper1987-oss/quantlix"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 rounded-lg border border-slate-800 px-4 py-2 hover:border-slate-600 hover:text-slate-300"
          >
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            GitHub
          </a>
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Deployed by developers at startups & labs
          </span>
          <blockquote className="max-w-md text-sm italic text-slate-500">
            &ldquo;Deploy FastAPI + PyTorch in 30 seconds. No cloud config.&rdquo;
          </blockquote>
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

      {/* 3b. Use cases */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="mb-8 text-center text-2xl font-semibold text-slate-100">
          Use cases
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[
            {
              title: "PyTorch model API",
              desc: "Deploy PyTorch models as production-ready REST APIs in seconds.",
            },
            {
              title: "FastAPI deployments",
              desc: "Serve FastAPI apps with auto-scaling and zero infra management.",
            },
            {
              title: "HuggingFace inference",
              desc: "Run HuggingFace models in production. GPU support available.",
            },
          ].map((u) => (
            <div
              key={u.title}
              className="rounded-lg border border-slate-800 bg-slate-900/30 p-5"
            >
              <h3 className="font-medium text-slate-200">{u.title}</h3>
              <p className="mt-1 text-sm text-slate-500">{u.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 4. Live demo + Code example */}
      <section id="live-demo" className="mx-auto max-w-6xl px-4 py-24 scroll-mt-24">
        <h2 className="mb-4 text-center text-2xl font-semibold text-slate-100">
          Try a live demo
        </h2>
        <p className="mb-12 text-center text-slate-400">
          See the API response without signing up. Then deploy your own.
        </p>
        <LiveDemo />
      </section>

      {/* 4b. Code example (kept for copy-paste) */}
      <section className="mx-auto max-w-6xl px-4 py-16">
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

      {/* 5b. Why Quantlix is fast */}
      <section className="mx-auto max-w-6xl px-4 py-24">
        <h2 className="mb-12 text-center text-2xl font-semibold text-slate-100">
          Why Quantlix is fast
        </h2>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[
            {
              title: "Auto-scaling",
              desc: "Scale to zero when idle. Cold start ~20s on free tier, instant on Pro.",
            },
            {
              title: "CPU & GPU",
              desc: "Choose CPU for cost or GPU for speed. Pro includes 2h GPU/month.",
            },
            {
              title: "Latency",
              desc: "<50ms inference for warm deployments. EU-hosted for low latency.",
            },
            {
              title: "Error handling",
              desc: "Structured errors, retries, and deployment logs in the dashboard.",
            },
            {
              title: "Performance",
              desc: "Optimized for inference. No cold starts on Pro priority queue.",
            },
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
        <div className="mb-12 flex justify-center">
          <CostCalculator />
        </div>
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
            pip install quantlix
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <a href="#live-demo">
              <Button variant="outline" size="lg">
                Try demo (no signup)
              </Button>
            </a>
            <Link href="/signup">
              <Button variant="primary" size="lg">
                Get started
              </Button>
            </Link>
            <Link href="/docs">
              <Button variant="secondary" size="lg">
                View docs
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
