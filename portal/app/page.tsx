import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CopyButton } from "@/components/copy-button";
import { CostCalculator } from "@/components/cost-calculator";
import { LiveDemo } from "@/components/live-demo";

export default function Home() {
  return (
    <main>
      {/* HERO — live system interface preview */}
      <section className="relative mx-auto max-w-4xl px-4 pt-[120px] pb-20 md:pt-[140px] md:pb-24 overflow-hidden">
        {/* Subtle background grid */}
        <div className="pipeline-grid absolute inset-0 opacity-[0.04]" aria-hidden />
        <div className="relative text-center space-y-6">
          <p className="text-xs font-medium uppercase tracking-[0.25em] text-slate-500">
            Quantlix runtime platform
          </p>
          <h1 className="text-4xl font-semibold tracking-tight text-slate-50 md:text-5xl lg:text-6xl">
            Deploy AI models instantly. Run them reliably.
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-slate-500 md:text-xl">
            With built-in guardrails and predictable costs.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link href="/signup">
              <Button
                variant="primary"
                size="lg"
                className="shadow-[0_0_24px_-4px_rgba(168,85,247,0.4)] ring-1 ring-white/10"
              >
                Deploy a Model
              </Button>
            </Link>
            <Link href="/docs">
              <Button variant="outline" size="lg">
                View Docs
              </Button>
            </Link>
          </div>
          <p className="text-sm text-slate-600">
            Guardrails • Retry control • Cost visibility • Rate limits •
            Observability
          </p>
          {/* Terminal preview */}
          <div className="mx-auto max-w-sm rounded-lg border border-slate-700/80 bg-slate-950/80 px-4 py-3 font-mono text-left text-xs text-slate-400">
            <div className="text-slate-500">$ quantlix deploy model.pt</div>
            <div className="mt-1 text-emerald-500/90">✓ validated</div>
            <div className="text-emerald-500/90">✓ runtime provisioned</div>
            <div className="text-emerald-500/90">✓ endpoint live</div>
          </div>
          {/* Live system status */}
          <div className="flex flex-wrap items-center justify-center gap-6 pt-2 font-mono text-xs text-slate-500">
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_6px_2px_rgba(52,211,153,0.5)]" />
              Runtime healthy
            </span>
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_6px_2px_rgba(52,211,153,0.5)]" />
              Policies active
            </span>
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_6px_2px_rgba(52,211,153,0.5)]" />
              Scaling ready
            </span>
          </div>
        </div>
      </section>

      {/* RUNTIME GUARANTEES — capability bar */}
      <section className="relative border-y border-slate-800 py-[60px] overflow-hidden">
        {/* Subtle background */}
        <div className="pipeline-grid absolute inset-0 opacity-60" aria-hidden />
        <div className="absolute inset-0 bg-gradient-to-b from-slate-900/40 via-transparent to-slate-900/40" aria-hidden />
        <div className="relative mx-auto max-w-4xl px-4">
          <p className="mb-6 text-center text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
            Runtime guarantees
          </p>
          <div className="flex flex-nowrap items-center justify-center gap-3 overflow-x-auto pb-2 md:overflow-visible md:pb-0">
            {[
              {
                label: "Serverless runtime",
                dot: "bg-emerald-500",
                glow: "shadow-[0_0_12px_-2px_rgba(52,211,153,0.3)]",
                border: "border-emerald-500/25",
                title: "No VM provisioning",
              },
              {
                label: "Auto scaling workers",
                dot: "bg-cyan-500",
                glow: "shadow-[0_0_12px_-2px_rgba(34,211,238,0.3)]",
                border: "border-cyan-500/25",
                title: "Dynamic worker allocation",
              },
              {
                label: "Managed execution",
                dot: "bg-violet-500",
                glow: "shadow-[0_0_12px_-2px_rgba(139,92,246,0.3)]",
                border: "border-violet-500/25",
                title: "Auto environment provisioning",
              },
              {
                label: "Production-grade safeguards",
                dot: "bg-blue-500",
                glow: "shadow-[0_0_12px_-2px_rgba(59,130,246,0.3)]",
                border: "border-blue-500/25",
                title: "Built-in guardrails + policies",
              },
            ].map((item) => (
              <span
                key={item.label}
                title={item.title}
                className={`group flex flex-shrink-0 items-center gap-2 rounded-full border px-4 py-2 font-mono text-xs font-medium text-slate-300 transition hover:border-opacity-50 hover:text-slate-200 ${item.border} ${item.glow} bg-slate-900/60`}
              >
                <span
                  className={`h-2 w-2 flex-shrink-0 rounded-full ${item.dot} shadow-sm`}
                  aria-hidden
                />
                <span>✓</span>
                <span>{item.label}</span>
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS — Deployment pipeline */}
      <section className="relative mx-auto max-w-6xl px-4 py-20 overflow-hidden">
        {/* Subtle grid background */}
        <div className="pipeline-grid absolute inset-0" aria-hidden />
        <div className="relative">
          <p className="mb-2 text-center text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
            Deployment pipeline
          </p>
          <h2 className="mb-16 text-center text-2xl font-semibold text-slate-100 md:text-3xl">
            How your model goes live
          </h2>

          {/* Timeline + pipeline */}
          <div className="flex flex-col items-center gap-8 md:flex-row md:items-stretch md:justify-center md:gap-0">
            {[
              {
                label: "UPLOAD",
                title: "Register your model",
                meta: [".pt / .onnx supported", "validated automatically"],
                status: "READY",
                statusColor: "text-cyan-400 border-cyan-500/30 bg-cyan-500/10",
                cardGlow: "shadow-[0_0_20px_-5px_rgba(34,211,238,0.15)]",
                border: "border-cyan-500/25",
                bg: "bg-slate-900/60",
              },
              {
                label: "DEPLOY",
                title: "Runtime provisioned",
                meta: ["Workers allocated", "Policies applied"],
                status: "DEPLOYING",
                statusColor: "text-violet-400 border-violet-500/30 bg-violet-500/10",
                cardGlow: "shadow-[0_0_20px_-5px_rgba(139,92,246,0.2)]",
                border: "border-violet-500/25",
                bg: "bg-slate-900/60",
              },
              {
                label: "LIVE ENDPOINT",
                title: "Ready for traffic",
                meta: ["Latency: <50ms", "Status: healthy"],
                status: "ACTIVE",
                statusColor: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10",
                cardGlow: "shadow-[0_0_20px_-5px_rgba(52,211,153,0.2)]",
                border: "border-emerald-500/25",
                bg: "bg-slate-900/60",
              },
            ].map((item, i) => (
              <div
                key={item.label}
                className="flex flex-col items-center md:flex-row"
              >
                <div
                  className={`w-full max-w-[280px] rounded-xl border p-6 ${item.border} ${item.bg} ${item.cardGlow} transition hover:shadow-lg`}
                >
                  <div className="mb-3 flex items-center justify-between">
                    <span className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-400">
                      {item.label}
                    </span>
                    <span
                      className={`rounded border px-2 py-0.5 font-mono text-[10px] font-medium ${item.statusColor}`}
                    >
                      {item.status}
                    </span>
                  </div>
                  <h3 className="font-medium text-slate-200">{item.title}</h3>
                  <ul className="mt-3 space-y-1">
                    {item.meta.map((m) => (
                      <li
                        key={m}
                        className="font-mono text-xs text-slate-500"
                      >
                        {m}
                      </li>
                    ))}
                  </ul>
                </div>
                {i < 2 && (
                  <div className="flex flex-shrink-0 items-center py-6 md:py-0 md:px-3">
                    <div className="flex items-center gap-0">
                      <span className="h-1.5 w-1.5 rounded-full bg-slate-500/80" />
                      <div
                        className={`h-px w-12 md:w-16 ${
                          i === 0
                            ? "bg-gradient-to-r from-cyan-500/50 via-slate-500/40 to-violet-500/50"
                            : "bg-gradient-to-r from-violet-500/50 via-slate-500/40 to-emerald-500/50"
                        }`}
                        style={{
                          animation: "pipeline-glow 2.5s ease-in-out infinite",
                          boxShadow:
                            i === 0
                              ? "0 0 10px 1px rgba(34,211,238,0.15)"
                              : "0 0 10px 1px rgba(52,211,153,0.15)",
                        }}
                      />
                      <span className="h-1.5 w-1.5 rounded-full bg-slate-500/80" />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          <p className="mt-10 text-center text-sm text-slate-500">
            No infrastructure setup required
          </p>
        </div>
      </section>

      {/* PRODUCTION SECTION — 80px */}
      <section className="mx-auto max-w-6xl px-4 py-20">
        <h2 className="mb-16 text-center text-2xl font-semibold text-slate-100 md:text-3xl">
          Deployment is easy. Production is hard.
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { title: "Guardrails", desc: "Block unsafe inputs" },
            { title: "Retry Control", desc: "Prevent runaway costs" },
            { title: "Rate Limits", desc: "Protect against abuse" },
            { title: "Policy Engine", desc: "Enforce runtime rules" },
            { title: "Metrics", desc: "See what's happening" },
            { title: "Tracing", desc: "Debug end-to-end" },
          ].map((f) => (
            <div
              key={f.title}
              className="rounded-lg border border-slate-800 bg-slate-900/30 p-6"
            >
              <h3 className="font-medium text-slate-200">{f.title}</h3>
              <p className="mt-1 text-sm text-slate-500">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* COST VISIBILITY — 80px */}
      <section className="mx-auto max-w-6xl px-4 py-20">
        <h2 className="mb-6 text-center text-2xl font-semibold text-slate-100 md:text-3xl">
          Know your real inference cost
        </h2>
        <p className="mx-auto mb-12 max-w-xl text-center text-slate-400">
          Retries and fallbacks can silently multiply usage.
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: "tokens used" },
            { label: "retry count" },
            { label: "cost multiplier" },
            { label: "blocked requests" },
          ].map((m) => (
            <div
              key={m.label}
              className="rounded-lg border border-slate-800 bg-slate-900/30 px-6 py-4 text-center"
            >
              <span className="text-sm font-medium text-slate-300">
                {m.label}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* PROBLEM SECTION — 80px */}
      <section className="mx-auto max-w-6xl px-4 py-20">
        <h2 className="mb-12 text-center text-2xl font-semibold text-slate-100 md:text-3xl">
          What breaks when traffic hits
        </h2>
        <ul className="mx-auto max-w-md space-y-4 text-slate-400">
          {[
            "Costs spike",
            "Retries multiply calls",
            "Bad inputs reach models",
            "Latency fluctuates",
            "Scaling gets fragile",
          ].map((item) => (
            <li key={item} className="flex items-center gap-3">
              <span className="h-2 w-2 rounded-full bg-amber-500/60" />
              {item}
            </li>
          ))}
        </ul>
      </section>

      {/* POSITIONING BLOCK — 80px */}
      <section className="mx-auto max-w-4xl px-4 py-20">
        <h2 className="text-center text-2xl font-semibold text-slate-100 md:text-3xl leading-relaxed">
          Quantlix is not just a deployment platform — it's a runtime control
          layer for AI workloads.
        </h2>
      </section>

      {/* WHO IT'S FOR — 80px */}
      <section className="mx-auto max-w-6xl px-4 py-20">
        <h2 className="mb-12 text-center text-2xl font-semibold text-slate-100 md:text-3xl">
          Who it's for
        </h2>
        <div className="flex flex-wrap items-center justify-center gap-4 text-slate-400">
          {["LLM Builders", "ML Engineers", "AI Startups", "Product Teams"].map(
            (item) => (
              <span
                key={item}
                className="rounded-full border border-slate-700 bg-slate-900/50 px-5 py-2 text-sm"
              >
                {item}
              </span>
            )
          )}
        </div>
      </section>

      {/* TECH STRIP — 60px, subtle */}
      <section className="border-y border-slate-800 bg-slate-900/20 py-[60px]">
        <div className="mx-auto max-w-4xl px-4 text-center text-sm text-slate-500">
          guardrails • policy engine • retry control • cost tracking • tracing
        </div>
      </section>

      {/* PRICING TRANSITION — 60px */}
      <section className="mx-auto max-w-6xl px-4 py-[60px]">
        <p className="text-center text-lg text-slate-400">
          Start free. Scale when you're ready.
        </p>
      </section>

      {/* FINAL CTA — 80px */}
      <section className="mx-auto max-w-6xl px-4 py-20">
        <div className="rounded-xl border border-slate-800 bg-slate-900/30 px-8 py-20 text-center">
          <h2 className="text-2xl font-semibold text-slate-100 md:text-3xl">
            Deploy your first model today
          </h2>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link href="/signup">
              <Button variant="primary" size="lg">
                Start Deploying
              </Button>
            </Link>
            <Link href="/signup">
              <Button variant="outline" size="lg">
                Get API Key
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Secondary: Live Demo */}
      <section
        id="live-demo"
        className="mx-auto max-w-6xl px-4 py-20 scroll-mt-24"
      >
        <h2 className="mb-4 text-center text-2xl font-semibold text-slate-100">
          Try a live demo
        </h2>
        <p className="mb-12 text-center text-slate-400">
          See the API response without signing up.
        </p>
        <LiveDemo />
      </section>

      {/* Secondary: Code + Pricing */}
      <section className="mx-auto max-w-6xl px-4 py-20">
        <h2 className="mb-6 text-center text-2xl font-semibold text-slate-100">
          Copy-paste cURL example
        </h2>
        <div className="relative mx-auto max-w-2xl rounded-lg border border-slate-800 bg-slate-900/50 p-6 font-mono text-sm">
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
        <div className="mt-16 flex justify-center">
          <CostCalculator />
        </div>
        <div className="mt-8 grid gap-6 md:grid-cols-4">
          {[
            { name: "Free", price: "€0", desc: "100k tokens, 1h compute" },
            {
              name: "Starter",
              price: "€9/mo",
              desc: "500k tokens, 5h compute",
            },
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
    </main>
  );
}
