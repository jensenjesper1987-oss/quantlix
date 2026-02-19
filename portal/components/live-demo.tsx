"use client";

import { useState } from "react";
import { CopyButton } from "@/components/copy-button";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.quantlix.ai";

const SAMPLE_RESPONSE = `{
  "output_data": {
    "generated": "Hello, world! How are you doing today?",
    "model": "qx-example"
  },
  "tokens_used": 12,
  "compute_seconds": 0.04
}`;

const DEMO_CURL = `curl -X POST ${API_URL}/demo \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "Hello, world!"}'`;

const CURL_CMD = `curl -X POST ${API_URL}/run \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"deployment_id": "YOUR_DEPLOYMENT_ID", "input": {"prompt": "Hello, world!"}}'`;

export function LiveDemo() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function runDemo() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_URL}/demo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: "Hello, world!" }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setResult(JSON.stringify(data, null, 2));
      } else {
        setError(
          res.status === 404
            ? "Demo endpoint not yet deployed. Sample response below:"
            : data.detail || "Demo unavailable"
        );
        setResult(SAMPLE_RESPONSE);
      }
    } catch {
      setError("Could not reach API. Sample response below:");
      setResult(SAMPLE_RESPONSE);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-6 font-mono text-sm">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-slate-400">Request (no API key needed)</span>
          <CopyButton text={DEMO_CURL} />
        </div>
        <pre className="overflow-x-auto text-slate-300">{DEMO_CURL}</pre>
      </div>
      <div className="flex flex-wrap gap-3">
        <button
          onClick={runDemo}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg bg-[#A855F7] px-4 py-2 text-sm font-medium text-white hover:bg-[#9333ea] disabled:opacity-50"
        >
          {loading ? (
            <>
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Running…
            </>
          ) : (
            "Try live demo (no signup)"
          )}
        </button>
      </div>
      {(result || error) && (
        <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-6 font-mono text-sm">
          <div className="mb-2 text-slate-400">Response</div>
          {error && (
            <p className="mb-3 text-sm text-amber-400/90">{error}</p>
          )}
          <pre className="overflow-x-auto text-slate-300">
            {result || SAMPLE_RESPONSE}
          </pre>
        </div>
      )}
      {!result && !error && (
        <div className="rounded-lg border border-slate-800/50 bg-slate-900/30 p-6 font-mono text-sm">
          <div className="mb-2 text-slate-500">Response (sample)</div>
          <pre className="overflow-x-auto text-slate-500">{SAMPLE_RESPONSE}</pre>
        </div>
      )}
    </div>
  );
}
