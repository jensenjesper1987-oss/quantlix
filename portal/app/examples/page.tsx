import Link from "next/link";
import { CopyButton } from "@/components/copy-button";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.quantlix.ai";

export const metadata = {
  title: "Examples — Quantlix",
  description:
    "Public example deployments with real metrics. Deploy time, latency, cost.",
};

const EXAMPLES = [
  {
    id: "qx-example",
    model: "DistilGPT-2",
    deployTime: "~12s",
    latency: "<50ms",
    cost: "Free tier",
    deploymentId: "dade526b-7a87-4759-ba6d-f97c83895607",
    description: "Lightweight text generation. Good for demos and prototyping.",
  },
  {
    id: "qx-example-gpu",
    model: "DistilGPT-2 (GPU)",
    deployTime: "~18s",
    latency: "<30ms",
    cost: "Pro: €0.50/hr",
    deploymentId: "YOUR_DEPLOYMENT_ID",
    description:
      "Same model on GPU for lower latency. Pro plan includes 2h/month.",
  },
];

export default function ExamplesPage() {
  return (
    <main className="mx-auto max-w-5xl px-4 py-16">
      <h1 className="text-3xl font-semibold text-slate-100">
        Public example deployments
      </h1>
      <p className="mt-4 text-slate-400">
        Real deployments with real metrics. Try them with your API key.
      </p>

      <div className="mt-12 overflow-hidden rounded-xl border border-slate-800">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/50">
              <th className="px-6 py-4 text-xs font-medium uppercase tracking-wider text-slate-500">
                Model
              </th>
              <th className="px-6 py-4 text-xs font-medium uppercase tracking-wider text-slate-500">
                Deploy time
              </th>
              <th className="px-6 py-4 text-xs font-medium uppercase tracking-wider text-slate-500">
                Latency
              </th>
              <th className="px-6 py-4 text-xs font-medium uppercase tracking-wider text-slate-500">
                Cost
              </th>
              <th className="px-6 py-4 text-xs font-medium uppercase tracking-wider text-slate-500">
                Endpoint
              </th>
            </tr>
          </thead>
          <tbody>
            {EXAMPLES.map((ex) => (
              <tr
                key={ex.id}
                className="border-b border-slate-800/50 last:border-0 hover:bg-slate-900/30"
              >
                <td className="px-6 py-4">
                  <div>
                    <span className="font-medium text-slate-200">
                      {ex.model}
                    </span>
                    <p className="mt-0.5 text-xs text-slate-500">
                      {ex.description}
                    </p>
                  </div>
                </td>
                <td className="px-6 py-4 font-mono text-sm text-slate-400">
                  {ex.deployTime}
                </td>
                <td className="px-6 py-4 font-mono text-sm text-slate-400">
                  {ex.latency}
                </td>
                <td className="px-6 py-4 text-sm text-slate-400">{ex.cost}</td>
                <td className="px-6 py-4">
                  <div className="flex flex-wrap items-center gap-3">
                    <CopyButton
                      inline
                      text={`curl -X POST ${API_URL}/run \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"deployment_id": "${ex.deploymentId}", "input": {"prompt": "Hello!"}}'`}
                    />
                    <Link
                      href={`${API_URL}/docs`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-[#A855F7] hover:underline"
                    >
                      API docs
                    </Link>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-8 rounded-lg border border-slate-800 bg-slate-900/30 p-6">
        <h2 className="font-medium text-slate-200">How to use</h2>
        <p className="mt-2 text-sm text-slate-500">
          Sign up to get an API key, then deploy the demo model from your
          dashboard. Use your deployment ID in the cURL command above. Metrics
          are from production deployments on Quantlix.
        </p>
        <div className="mt-4 flex gap-4">
          <Link
            href="/signup"
            className="rounded-lg border border-[#A855F7]/40 bg-[#A855F7]/10 px-4 py-2 text-sm font-medium text-[#A855F7] hover:bg-[#A855F7]/20"
          >
            Get API key
          </Link>
          <Link
            href="/dashboard"
            className="rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-2 text-sm text-slate-300 hover:bg-slate-700/50"
          >
            Deploy demo
          </Link>
        </div>
      </div>
    </main>
  );
}
