"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";

function SyncPlanButton({ onSynced }: { onSynced: () => void }) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function handleSync() {
    setLoading(true);
    setMessage(null);
    try {
      const res = await fetch("/api/billing/sync", { method: "POST" });
      const data = await res.json().catch(() => ({}));
      if (res.ok && (data.plan === "pro" || data.plan === "starter")) {
        onSynced();
      } else {
        setMessage(data.message || "No active subscription found.");
      }
    } catch {
      setMessage("Sync failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <span className="ml-2">
      <Button
        variant="ghost"
        size="sm"
        className="h-6 text-xs"
        onClick={handleSync}
        disabled={loading}
      >
        {loading ? "Syncing..." : "Sync subscription"}
      </Button>
      {message && (
        <span className="ml-1 text-xs text-amber-400">({message})</span>
      )}
    </span>
  );
}

function QuickstartSection({
  apiKey,
  apiUrl,
  plan,
}: {
  apiKey?: string;
  apiUrl: string;
  plan: string;
}) {
  const [deploymentId, setDeploymentId] = useState<string | null>(null);
  const [deploying, setDeploying] = useState(false);
  const [deployError, setDeployError] = useState<string | null>(null);
  const [curlCopied, setCurlCopied] = useState(false);
  const [cliCopied, setCliCopied] = useState(false);

  async function deployDemo() {
    setDeploying(true);
    setDeployError(null);
    try {
      const res = await fetch("/api/deploy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model_id: "qx-example" }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Deploy failed");
      const id = data.deployment_id;
      setDeploymentId(id);
      // Poll until ready (or give up after ~15s)
      for (let i = 0; i < 15; i++) {
        await new Promise((r) => setTimeout(r, 1000));
        const s = await fetch(`/api/status/${id}`).then((r) => r.json()).catch(() => ({}));
        if (s.status === "ready" || s.status === "READY") break;
      }
    } catch (e) {
      setDeployError(e instanceof Error ? e.message : "Deploy failed");
    } finally {
      setDeploying(false);
    }
  }

  const curlCmd =
    apiKey && deploymentId
      ? `curl -X POST ${apiUrl}/run \\
  -H "X-API-Key: ${apiKey}" \\
  -H "Content-Type: application/json" \\
  -d '{"deployment_id": "${deploymentId}", "input": {"prompt": "Hello, world!"}}'`
      : null;

  const cliCommands = apiKey
    ? `export QUANTLIX_API_KEY="${apiKey}"
export QUANTLIX_API_URL="${apiUrl}"
pip install quantlix
quantlix deploy qx-example
quantlix run <deployment_id> -i '{"prompt": "Hello!"}'`
    : `pip install quantlix
quantlix login
quantlix deploy qx-example --api-key <your_api_key>
quantlix run <deployment_id> -i '{"prompt": "Hello!"}' --api-key <your_api_key>`;

  async function copyCurl() {
    if (curlCmd) {
      await navigator.clipboard.writeText(curlCmd);
      setCurlCopied(true);
      setTimeout(() => setCurlCopied(false), 2000);
    }
  }

  async function copyCli() {
    await navigator.clipboard.writeText(cliCommands);
    setCliCopied(true);
    setTimeout(() => setCliCopied(false), 2000);
  }

  return (
    <section className="mb-8 rounded-lg border-2 border-[#A855F7]/40 bg-slate-900/50 p-6">
      {deploymentId ? (
        <>
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-slate-100">
              Your endpoint is live 🚀
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Run inference with the cURL below. Momentum drives usage.
            </p>
            {plan === "free" && (
              <p className="mt-2 text-xs text-slate-500">
                Free queue: ~20s · <Link href="/pricing" className="text-[#10B981] hover:text-[#10B981]/80">Starter/Pro: priority</Link>
              </p>
            )}
          </div>
          <div className="mb-6">
            <p className="mb-2 text-sm font-medium text-slate-300">Copy-paste cURL</p>
            <div className="relative rounded border border-slate-700 bg-slate-800/50 p-4 font-mono text-xs text-slate-300">
              <pre className="overflow-x-auto whitespace-pre-wrap break-all">
                {curlCmd}
              </pre>
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-2 top-2 h-7 text-xs"
                onClick={copyCurl}
              >
                {curlCopied ? "Copied!" : "Copy"}
              </Button>
            </div>
          </div>
          <div>
            <p className="mb-3 text-sm font-medium text-slate-300">What&apos;s next?</p>
            <div className="flex flex-wrap gap-3">
              <Link href="/docs">
                <Button variant="outline" size="sm">
                  Try another model
                </Button>
              </Link>
              <Link href="/docs">
                <Button variant="outline" size="sm">
                  Run batch inference
                </Button>
              </Link>
              <Link href="/pricing">
                <Button variant="outline" size="sm">
                  Deploy with GPU
                </Button>
              </Link>
            </div>
          </div>
        </>
      ) : (
        <>
          <h2 className="mb-2 text-lg font-medium text-slate-200">
            Get started in 60 seconds
          </h2>
          <p className="mb-6 text-sm text-slate-500">
            Deploy the demo model and run your first inference.
          </p>

          <div className="space-y-6">
            <div>
              <p className="mb-2 text-sm font-medium text-slate-300">1. Deploy demo model</p>
              <div className="mb-2 flex items-center gap-4 text-xs text-slate-500">
                <span>{plan === "free" ? "Free queue: ~20s" : "Priority queue"}</span>
                {plan === "free" && (
                  <Link href="/pricing" className="text-[#10B981] hover:text-[#10B981]/80">
                    Starter/Pro: priority →
                  </Link>
                )}
              </div>
              <Button
                variant="primary"
                size="sm"
                onClick={deployDemo}
                disabled={deploying}
              >
                {deploying ? "Deploying..." : "Deploy demo (one click)"}
              </Button>
              {deployError && (
                <p className="mt-2 text-sm text-red-400">{deployError}</p>
              )}
            </div>

            <div>
              <p className="mb-2 text-sm font-medium text-slate-300">
                2. Copy-paste cURL
              </p>
              <div className="rounded border border-slate-700 bg-slate-800/50 p-4 font-mono text-xs text-slate-500">
                # Deploy demo first, then your curl will appear here
              </div>
            </div>

            <div>
              <p className="mb-2 text-sm font-medium text-slate-300">
                3. CLI quickstart
              </p>
              <p className="mb-2 text-xs text-slate-500">
                API key required. The first run activates the deployment and moves it from pending to ready.
              </p>
              <div className="relative rounded border border-slate-700 bg-slate-800/50 p-4 font-mono text-xs text-slate-300">
                <pre className="overflow-x-auto whitespace-pre-wrap break-all">
                  {cliCommands}
                </pre>
                <Button
                  variant="ghost"
                  size="sm"
                  className="absolute right-2 top-2 h-7 text-xs"
                  onClick={copyCli}
                >
                  {cliCopied ? "Copied!" : "Copy"}
                </Button>
              </div>
            </div>
          </div>
        </>
      )}
    </section>
  );
}

type DeploymentItem = {
  id: string;
  model_id: string;
  status: string;
  created_at: string | null;
  updated_at: string | null;
  revision_count: number;
};

type RevisionItem = {
  revision_number: number;
  model_id: string;
  model_path: string | null;
  config: Record<string, unknown>;
  created_at: string | null;
};

function DeploymentsSection() {
  const [deployments, setDeployments] = useState<DeploymentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [revisions, setRevisions] = useState<Record<string, RevisionItem[]>>({});
  const [loadingRevisions, setLoadingRevisions] = useState<Set<string>>(new Set());
  const [rollbackLoading, setRollbackLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    fetch("/api/deployments")
      .then((r) => (r.ok ? r.json() : { deployments: [] }))
      .then((data) => setDeployments(data.deployments || []))
      .catch(() => setDeployments([]))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function loadRevisions(id: string) {
    if (revisions[id]) return;
    setLoadingRevisions((s) => new Set(s).add(id));
    try {
      const res = await fetch(`/api/deployments/${id}/revisions`);
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setRevisions((prev) => ({ ...prev, [id]: data.revisions || [] }));
      }
    } finally {
      setLoadingRevisions((s) => {
        const next = new Set(s);
        next.delete(id);
        return next;
      });
    }
  }

  function toggleExpand(id: string) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else {
        next.add(id);
        loadRevisions(id);
      }
      return next;
    });
  }

  async function handleRollback(deploymentId: string, revision: number) {
    const key = `${deploymentId}-${revision}`;
    setRollbackLoading(key);
    setError(null);
    try {
      const res = await fetch(
        `/api/deployments/${deploymentId}/rollback?revision=${revision}`,
        { method: "POST" }
      );
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Rollback failed");
      refresh();
      setRevisions((prev) => ({ ...prev, [deploymentId]: [] }));
      setExpanded((prev) => {
        const next = new Set(prev);
        next.delete(deploymentId);
        return next;
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Rollback failed");
    } finally {
      setRollbackLoading(null);
    }
  }

  if (loading) {
    return (
      <section className="mb-8 rounded-lg border border-slate-800 bg-slate-900/30 p-6">
        <h2 className="mb-4 text-lg font-medium text-slate-200">Deployments</h2>
        <div className="text-sm text-slate-500">Loading deployments...</div>
      </section>
    );
  }

  if (deployments.length === 0) {
    return (
      <section className="mb-8 rounded-lg border border-slate-800 bg-slate-900/30 p-6">
        <h2 className="mb-4 text-lg font-medium text-slate-200">Deployments</h2>
        <p className="text-sm text-slate-500">
          No deployments yet. Deploy a model via the quickstart above or CLI.
        </p>
      </section>
    );
  }

  return (
    <section className="mb-8 rounded-lg border border-slate-800 bg-slate-900/30 p-6">
      <h2 className="mb-4 text-lg font-medium text-slate-200">Deployments</h2>
      <p className="mb-4 text-sm text-slate-500">
        View revisions and rollback to a previous configuration.
      </p>
      {error && (
        <div className="mb-4 rounded border border-red-800/50 bg-red-950/30 p-3 text-sm text-red-400">
          {error}
        </div>
      )}
      <div className="space-y-2">
        {deployments.map((d) => (
          <div
            key={d.id}
            className="rounded border border-slate-700/50 bg-slate-800/30"
          >
            <button
              type="button"
              className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-slate-700/30"
              onClick={() => toggleExpand(d.id)}
            >
              <div className="flex items-center gap-3">
                <span className="font-mono text-sm text-slate-200">{d.model_id}</span>
                <span className="rounded-full border border-slate-600 px-2 py-0.5 text-xs text-slate-400">
                  {d.status}
                </span>
                {d.revision_count > 0 && (
                  <span className="text-xs text-slate-500">
                    {d.revision_count} revision{d.revision_count !== 1 ? "s" : ""}
                  </span>
                )}
              </div>
              <span className="text-slate-500">
                {expanded.has(d.id) ? "▼" : "▶"}
              </span>
            </button>
            {expanded.has(d.id) && (
              <div className="border-t border-slate-700/50 px-4 py-3">
                {loadingRevisions.has(d.id) ? (
                  <div className="text-sm text-slate-500">Loading revisions...</div>
                ) : (revisions[d.id]?.length ?? 0) > 0 ? (
                  <div className="space-y-2">
                    {revisions[d.id].map((r) => (
                      <div
                        key={r.revision_number}
                        className="flex items-center justify-between rounded bg-slate-900/50 px-3 py-2"
                      >
                        <div>
                          <span className="font-medium text-slate-300">
                            Revision {r.revision_number}
                          </span>
                          <span className="ml-2 text-xs text-slate-500">
                            {r.model_id}
                            {r.created_at
                              ? ` · ${new Date(r.created_at).toLocaleString()}`
                              : ""}
                          </span>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          className="h-7 text-xs"
                          onClick={() => handleRollback(d.id, r.revision_number)}
                          disabled={rollbackLoading === `${d.id}-${r.revision_number}`}
                        >
                          {rollbackLoading === `${d.id}-${r.revision_number}`
                            ? "Rolling back..."
                            : "Rollback"}
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">
                    No revision history. Update this deployment via CLI to create revisions.
                  </p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

function ApiKeyDisplay({ keyValue }: { keyValue: string }) {
  const [copied, setCopied] = useState(false);
  const [visible, setVisible] = useState(false);

  const displayValue = visible ? keyValue : "•".repeat(24) + keyValue.slice(-8);

  async function copyKey() {
    await navigator.clipboard.writeText(keyValue);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <code className="max-w-full break-all rounded bg-slate-800 px-2 py-1 font-mono text-xs text-slate-300">
        {displayValue}
      </code>
      <div className="flex gap-1">
        <Button
          variant="ghost"
          size="sm"
          className="h-7 text-xs"
          onClick={() => setVisible(!visible)}
        >
          {visible ? "Hide" : "Show"}
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="h-7 text-xs"
          onClick={copyKey}
        >
          {copied ? "Copied!" : "Copy"}
        </Button>
      </div>
    </div>
  );
}

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [user, setUser] = useState<{
    id: string;
    email: string;
    plan: string;
    api_key?: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/me")
      .then((r) => (r.ok ? r.json() : null))
      .then(setUser)
      .finally(() => setLoading(false));
  }, []);

  const success = searchParams.get("success");
  const canceled = searchParams.get("canceled");
  const checkoutError = searchParams.get("error") === "checkout";
  const checkoutCode = searchParams.get("code");

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="animate-pulse text-slate-500">Loading...</div>
      </div>
    );
  }

  if (!user) {
    router.push("/signup");
    return null;
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-12">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-100">Dashboard</h1>
      </div>

      {success && (
        <div className="mb-6 rounded-lg border border-emerald-800/50 bg-emerald-950/30 p-4 text-emerald-400">
          Payment successful. Your plan has been upgraded.
        </div>
      )}
      {canceled && (
        <div className="mb-6 rounded-lg border border-amber-800/50 bg-amber-950/30 p-4 text-amber-400">
          Checkout was canceled.
        </div>
      )}
      {checkoutError && (
        <div className="mb-6 rounded-lg border border-red-800/50 bg-red-950/30 p-4 text-red-400">
          {checkoutCode === "auth" && "Please log in again to upgrade."}
          {checkoutCode === "config" && "Billing is not configured. Contact support."}
          {checkoutCode === "network" && "Could not reach the API. Try again later."}
          {(!checkoutCode || checkoutCode === "failed") && "Checkout failed. Please try again or contact support."}
        </div>
      )}

      <QuickstartSection
        apiKey={user.api_key}
        apiUrl={process.env.NEXT_PUBLIC_API_URL || "https://api.quantlix.ai"}
        plan={user.plan}
      />

      <DeploymentsSection />

      <section className="mb-8 rounded-lg border border-slate-800 bg-slate-900/30 p-6">
        <h2 className="mb-4 text-lg font-medium text-slate-200">Performance</h2>
        <PerformanceMetrics />
      </section>

      <section className="mb-8 rounded-lg border border-slate-800 bg-slate-900/30 p-6">
        <h2 className="mb-4 text-lg font-medium text-slate-200">Usage over time</h2>
        <UsageGraph />
      </section>

      <div className="grid gap-8 lg:grid-cols-2">
        <section className="rounded-lg border border-slate-800 bg-slate-900/30 p-6">
          <h2 className="mb-4 text-lg font-medium text-slate-200">Account</h2>
          <div className="space-y-2 text-sm">
            <p className="text-slate-400">
              <span className="text-slate-300">Email:</span> {user.email}
            </p>
            <p className="text-slate-400">
              <span className="text-slate-300">Plan:</span>{" "}
              <span className="capitalize text-slate-200">{user.plan}</span>
              {user.plan === "free" && (
                <>
                  <span className="ml-2 rounded-full border border-amber-700/60 bg-amber-950/40 px-2 py-0.5 text-xs text-amber-400">
                    Free plan
                  </span>
                  <SyncPlanButton onSynced={() => window.location.reload()} />
                </>
              )}
            </p>
            {user.api_key && (
              <div className="pt-2">
                <p className="mb-1 text-slate-300">API key</p>
                <ApiKeyDisplay keyValue={user.api_key} />
              </div>
            )}
          </div>
        </section>

        <section className="rounded-lg border border-slate-800 bg-slate-900/30 p-6">
          <h2 className="mb-4 text-lg font-medium text-slate-200">Usage</h2>
          <UsageCard plan={user.plan} />
        </section>
      </div>

      <section className="mt-8 rounded-lg border border-slate-800 bg-slate-900/30 p-6">
        <h2 className="mb-4 text-lg font-medium text-slate-200">Logs</h2>
        <LogsSection plan={user.plan} realtime />
      </section>

      <section className="mt-8 rounded-lg border border-slate-800 bg-slate-900/30 p-6">
        <h2 className="mb-4 text-lg font-medium text-slate-200">Limits</h2>
        <LimitsSection plan={user.plan} />
      </section>

      <section className="mt-8 rounded-lg border border-slate-800 bg-slate-900/30 p-6">
        <h2 className="mb-4 text-lg font-medium text-slate-200">Billing</h2>
        {user.plan === "free" && success && (
          <div className="mb-4 rounded-lg border border-amber-800/50 bg-amber-950/30 p-3 text-amber-400">
            <p className="text-sm">
              Payment received but plan not updated yet?{" "}
              <SyncPlanButton onSynced={() => window.location.reload()} />
            </p>
          </div>
        )}
        <div className="flex flex-col gap-3 sm:flex-row">
          {user.plan === "free" && (
            <>
              <form action="/api/billing/checkout" method="post">
                <input type="hidden" name="plan" value="starter" />
                <Button variant="outline" size="lg" type="submit">
                  Starter €9/mo
                </Button>
                <p className="mt-1 text-xs text-slate-500">500k tokens · 5h compute · priority queue</p>
              </form>
              <form action="/api/billing/checkout" method="post">
                <input type="hidden" name="plan" value="pro" />
                <Button variant="primary" size="lg" type="submit">
                  Pro €19/mo
                </Button>
                <p className="mt-1 text-xs text-slate-500">1M tokens · 10h CPU · 2h GPU · instant</p>
              </form>
            </>
          )}
          <form action="/api/billing/portal" method="post">
            <Button variant="outline" size="lg">
              Manage payment methods & subscription
            </Button>
          </form>
        </div>
      </section>
    </main>
  );
}

function PerformanceMetrics() {
  const [metrics, setMetrics] = useState<{
    success_rate: number;
    total_jobs: number;
    avg_latency_s: number | null;
    p50_latency_s: number | null;
    p95_latency_s: number | null;
  } | null>(null);

  useEffect(() => {
    fetch("/api/usage/metrics?days=30")
      .then((r) => (r.ok ? r.json() : null))
      .then(setMetrics);
  }, []);

  if (!metrics) {
    return <div className="text-sm text-slate-500">Loading metrics...</div>;
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
      <div className="rounded border border-slate-700/50 bg-slate-800/30 p-4">
        <p className="text-xs font-medium text-slate-500">Success rate</p>
        <p className="mt-1 text-xl font-semibold text-slate-100">
          {(metrics.success_rate * 100).toFixed(1)}%
        </p>
      </div>
      <div className="rounded border border-slate-700/50 bg-slate-800/30 p-4">
        <p className="text-xs font-medium text-slate-500">Total jobs (30d)</p>
        <p className="mt-1 text-xl font-semibold text-slate-100">{metrics.total_jobs}</p>
      </div>
      <div className="rounded border border-slate-700/50 bg-slate-800/30 p-4">
        <p className="text-xs font-medium text-slate-500">Avg latency</p>
        <p className="mt-1 text-xl font-semibold text-slate-100">
          {metrics.avg_latency_s != null ? `${metrics.avg_latency_s}s` : "—"}
        </p>
      </div>
      <div className="rounded border border-slate-700/50 bg-slate-800/30 p-4">
        <p className="text-xs font-medium text-slate-500">P50 latency</p>
        <p className="mt-1 text-xl font-semibold text-slate-100">
          {metrics.p50_latency_s != null ? `${metrics.p50_latency_s}s` : "—"}
        </p>
      </div>
      <div className="rounded border border-slate-700/50 bg-slate-800/30 p-4">
        <p className="text-xs font-medium text-slate-500">P95 latency</p>
        <p className="mt-1 text-xl font-semibold text-slate-100">
          {metrics.p95_latency_s != null ? `${metrics.p95_latency_s}s` : "—"}
        </p>
      </div>
    </div>
  );
}

function UsageGraph() {
  const [history, setHistory] = useState<{ daily: { date: string; tokens_used: number; compute_seconds: number; job_count: number }[] } | null>(null);

  useEffect(() => {
    fetch("/api/usage/history?days=30")
      .then((r) => (r.ok ? r.json() : null))
      .then(setHistory);
  }, []);

  if (!history || history.daily.length === 0) {
    return (
      <div className="text-sm text-slate-500">
        {history?.daily?.length === 0 ? "No usage data yet. Run some inferences to see your usage graph." : "Loading..."}
      </div>
    );
  }

  const maxTokens = Math.max(1, ...history.daily.map((d) => d.tokens_used));
  const maxCompute = Math.max(1, ...history.daily.map((d) => d.compute_seconds));

  return (
    <div className="space-y-4">
      <div className="flex gap-1 overflow-x-auto pb-2" style={{ minHeight: 120 }}>
        {history.daily.map((d) => (
          <div
            key={d.date}
            className="flex min-w-[24px] flex-1 flex-col items-center gap-1"
            title={`${d.date}: ${d.tokens_used.toLocaleString()} tokens, ${Math.round(d.compute_seconds)}s compute`}
          >
            <div className="flex w-full flex-1 flex-col justify-end gap-0.5">
              <div
                className="w-full rounded-t bg-[#A855F7]/60 transition-all hover:bg-[#A855F7]/80"
                style={{ height: `${Math.max(4, (d.tokens_used / maxTokens) * 80)}%` }}
              />
              <div
                className="w-full rounded-t bg-[#10B981]/50 transition-all hover:bg-[#10B981]/70"
                style={{ height: `${Math.max(4, (d.compute_seconds / maxCompute) * 80)}%` }}
              />
            </div>
            <span className="text-[10px] text-slate-500">
              {new Date(d.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
            </span>
          </div>
        ))}
      </div>
      <div className="flex gap-4 text-xs text-slate-500">
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded bg-[#A855F7]/60" /> Tokens
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded bg-[#10B981]/50" /> Compute (s)
        </span>
      </div>
    </div>
  );
}

function LogsSection({ plan, realtime }: { plan: string; realtime?: boolean }) {
  const [jobs, setJobs] = useState<
    { id: string; deployment_id: string; status: string; tokens_used: number | null; compute_seconds: number | null; created_at: string | null }[]
  >([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    fetch("/api/jobs")
      .then((r) => (r.ok ? r.json() : { jobs: [] }))
      .then((data) => setJobs(data.jobs || []))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!realtime) return;
    const id = setInterval(refresh, 5000);
    return () => clearInterval(id);
  }, [realtime, refresh]);

  if (loading) {
    return <div className="text-sm text-slate-500">Loading logs...</div>;
  }

  return (
    <div className="space-y-3">
      {realtime && (
        <p className="text-xs text-slate-500">Auto-refreshing every 5s</p>
      )}
      {plan === "free" && (
        <p className="text-xs text-slate-500">
          Free queue: ~20s · <Link href="/pricing" className="text-[#10B981] hover:text-[#10B981]/80">Starter/Pro: priority</Link>
        </p>
      )}
      {jobs.length === 0 ? (
        <p className="text-sm text-slate-500">No inference runs yet. Deploy a model and run your first inference.</p>
      ) : (
        <div className="max-h-48 overflow-y-auto rounded border border-slate-700/50 bg-slate-800/30">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 text-left">
                <th className="px-3 py-2 font-medium text-slate-400">Job</th>
                <th className="px-3 py-2 font-medium text-slate-400">Status</th>
                <th className="px-3 py-2 font-medium text-slate-400">Tokens</th>
                <th className="px-3 py-2 font-medium text-slate-400">Time</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((j) => (
                <tr key={j.id} className="border-b border-slate-700/50 last:border-0">
                  <td className="px-3 py-2 font-mono text-xs text-slate-300">{j.id.slice(0, 8)}…</td>
                  <td className="px-3 py-2">
                    <span
                      className={
                        j.status === "completed" || j.status === "COMPLETED"
                          ? "text-emerald-400"
                          : j.status === "failed" || j.status === "FAILED"
                            ? "text-red-400"
                            : "text-slate-400"
                      }
                    >
                      {j.status}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-slate-400">{j.tokens_used ?? "—"}</td>
                  <td className="px-3 py-2 text-slate-400">
                    {j.compute_seconds != null ? `${Math.round(j.compute_seconds)}s` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function LimitsSection({ plan }: { plan: string }) {
  const [usage, setUsage] = useState<{
    tokens_limit: number | null;
    compute_limit: number | null;
    gpu_limit: number | null;
  } | null>(null);

  useEffect(() => {
    fetch("/api/usage")
      .then((r) => (r.ok ? r.json() : null))
      .then(setUsage);
  }, []);

  if (!usage) {
    return <div className="text-sm text-slate-500">Loading limits...</div>;
  }

  const limits = [
    { label: "Tokens", value: usage.tokens_limit, unit: "this month", fmt: (v: number) => v.toLocaleString() },
    { label: "CPU compute", value: usage.compute_limit, unit: "s this month", fmt: (v: number) => `${Math.round(v)}s` },
    { label: "GPU", value: usage.gpu_limit, unit: "h this month", fmt: (v: number) => `${(v / 3600).toFixed(1)}h` },
  ];

  return (
    <div className="space-y-3">
      {(plan === "free" || plan === "starter") && (
        <p className="text-sm text-slate-500">
          {plan === "free" ? "Upgrade for higher limits and priority queue." : "Upgrade to Pro for GPU and higher limits."}{" "}
          <Link href="/pricing">
            <Button variant="outline" size="sm" className="mt-1">
              Unlock faster deploy
            </Button>
          </Link>
        </p>
      )}
      <div className="space-y-2 text-sm">
        {limits.map((l) => (
          <p key={l.label} className="text-slate-400">
            <span className="text-slate-300">{l.label}:</span>{" "}
            {l.value != null && l.value > 0
              ? `${l.fmt(l.value)} ${l.unit}`
              : l.label === "GPU"
                ? "Pro only"
                : "Unlimited"}
          </p>
        ))}
      </div>
    </div>
  );
}

function UsageCard({ plan }: { plan: string }) {
  const [usage, setUsage] = useState<{
    tokens_used: number;
    compute_seconds: number;
    gpu_seconds: number;
    tokens_limit: number | null;
    compute_limit: number | null;
    gpu_limit: number | null;
    gpu_seconds_overage: number | null;
  } | null>(null);

  useEffect(() => {
    fetch("/api/usage")
      .then((r) => (r.ok ? r.json() : null))
      .then(setUsage);
  }, []);

  if (!usage) {
    return (
      <div className="text-sm text-slate-500">Loading usage...</div>
    );
  }

  const approachingLimit =
    (plan === "free" || plan === "starter") &&
    [
      usage.tokens_limit != null && usage.tokens_limit > 0
        ? usage.tokens_used / usage.tokens_limit
        : 0,
      usage.compute_limit != null && usage.compute_limit > 0
        ? usage.compute_seconds / usage.compute_limit
        : 0,
      usage.gpu_limit != null && usage.gpu_limit > 0
        ? usage.gpu_seconds / usage.gpu_limit
        : 0,
    ].some((r) => r >= 0.7 && r <= 1);

  return (
    <div className="space-y-2 text-sm">
      {approachingLimit && (
        <div className="mb-4 rounded-lg border border-amber-800/50 bg-amber-950/30 p-3 text-amber-400">
          <p className="text-sm">
            You&apos;re approaching your limit. Upgrade to keep running models without interruption.
          </p>
          <Link href="/pricing">
            <Button variant="outline" size="sm" className="mt-2">
              Unlock faster deploy
            </Button>
          </Link>
        </div>
      )}
      <p className="text-slate-400">
        <span className="text-slate-300">Tokens:</span>{" "}
        {usage.tokens_used.toLocaleString()}
        {usage.tokens_limit != null && (
          <span className="text-slate-500">
            {" "}/ {usage.tokens_limit.toLocaleString()} this month
          </span>
        )}
      </p>
      <p className="text-slate-400">
        <span className="text-slate-300">CPU compute:</span>{" "}
        {Math.round(usage.compute_seconds)}s
        {usage.compute_limit != null && (
          <span className="text-slate-500">
            {" "}/ {Math.round(usage.compute_limit)}s this month
          </span>
        )}
      </p>
      {(usage.gpu_limit != null || usage.gpu_seconds > 0) && (
        <p className="text-slate-400">
          <span className="text-slate-300">GPU:</span>{" "}
          {(usage.gpu_seconds / 3600).toFixed(2)}h
          {usage.gpu_limit != null && (
            <span className="text-slate-500">
              {" "}/ {(usage.gpu_limit / 3600).toFixed(1)}h this month
            </span>
          )}
          {usage.gpu_seconds_overage != null && usage.gpu_seconds_overage > 0 && (
            <span className="text-amber-400">
              {" "}(+{(usage.gpu_seconds_overage / 3600).toFixed(2)}h overage @ €0.50/hr)
            </span>
          )}
        </p>
      )}
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[60vh] flex items-center justify-center">
          <div className="animate-pulse text-slate-500">Loading...</div>
        </div>
      }
    >
      <DashboardContent />
    </Suspense>
  );
}
