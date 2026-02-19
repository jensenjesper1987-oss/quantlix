import Link from "next/link";
import { CopyButton } from "@/components/copy-button";

const COMMANDS = [
  {
    category: "Auth",
    commands: [
      {
        cmd: "quantlix signup",
        opts: ["--email, -e", "--password, -p", "--url"],
        desc: "Create a new account. A verification email will be sent — click the link to get your API key.",
      },
      {
        cmd: "quantlix verify <token>",
        opts: ["--url"],
        desc: "Verify email and get API key. Use the token from the verification link.",
      },
      {
        cmd: "quantlix resend-verification",
        opts: ["--email, -e", "--url"],
        desc: "Resend verification email.",
      },
      {
        cmd: "quantlix login",
        opts: ["--email, -e", "--password, -p", "--url", "--verbose, -v"],
        desc: "Log in. Returns API key — set QUANTLIX_API_KEY in your environment.",
      },
      {
        cmd: "quantlix forgot-password",
        opts: ["--email, -e", "--url"],
        desc: "Request password reset. Check your inbox for the reset link.",
      },
      {
        cmd: "quantlix reset-password <token>",
        opts: ["--password, -p", "--url"],
        desc: "Reset password using token from the email link.",
      },
    ],
  },
  {
    category: "API keys",
    commands: [
      {
        cmd: "quantlix api-keys",
        opts: ["--api-key, -k", "--url"],
        desc: "List API keys for your account.",
      },
      {
        cmd: "quantlix create-api-key",
        opts: ["--name, -n", "--api-key, -k", "--url"],
        desc: "Create a new API key. The key is shown only once — save it.",
      },
      {
        cmd: "quantlix revoke-api-key <key_id>",
        opts: ["--api-key, -k", "--url"],
        desc: "Revoke an API key. It will stop working immediately.",
      },
      {
        cmd: "quantlix rotate-api-key",
        opts: ["--api-key, -k", "--url"],
        desc: "Create a new API key and revoke the current one. Update QUANTLIX_API_KEY with the new key.",
      },
    ],
  },
  {
    category: "Deploy",
    commands: [
      {
        cmd: "quantlix deploy <model_id>",
        opts: ["--model-path, -p", "--config, -c", "--gpu, -g", "--update", "--api-key, -k", "--url"],
        desc: "Deploy a model to the inference platform. Use --update <deployment_id> to update an existing deployment (creates a new revision).",
      },
      {
        cmd: "quantlix deployments",
        opts: ["--limit, -n", "--api-key, -k", "--url"],
        desc: "List deployments with revision counts.",
      },
      {
        cmd: "quantlix revisions <deployment_id>",
        opts: ["--api-key, -k", "--url"],
        desc: "List revisions for a deployment. Use quantlix rollback to restore a previous revision.",
      },
      {
        cmd: "quantlix rollback <deployment_id> <revision>",
        opts: ["--api-key, -k", "--url"],
        desc: "Rollback deployment to a previous revision.",
      },
    ],
  },
  {
    category: "Inference",
    commands: [
      {
        cmd: "quantlix run <deployment_id>",
        opts: ["--input, -i", "--api-key, -k", "--url"],
        desc: "Run inference on a deployed model. Input can be inline JSON or a path to a .json file.",
      },
      {
        cmd: "quantlix status <resource_id>",
        opts: ["--api-key, -k", "--url"],
        desc: "Get status of a deployment or job.",
      },
    ],
  },
  {
    category: "Usage",
    commands: [
      {
        cmd: "quantlix usage",
        opts: ["--start, -s", "--end, -e", "--api-key, -k", "--url"],
        desc: "Get usage stats (tokens, compute seconds, job count). Optionally filter by date range.",
      },
    ],
  },
];

export default function CliPage() {
  return (
    <main className="mx-auto max-w-4xl px-4 py-16">
      <h1 className="text-3xl font-semibold text-slate-100">
        CLI reference
      </h1>
      <p className="mt-4 text-slate-400">
        Complete list of Quantlix CLI commands. Install with{" "}
        <code className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-sm">
          pip install quantlix
        </code>
      </p>

      <div className="mt-4 rounded-lg border border-slate-700/50 bg-slate-800/30 p-4">
        <p className="text-sm text-slate-400">
          Most commands require an API key. Set{" "}
          <code className="rounded bg-slate-700/50 px-1 font-mono text-xs">
            QUANTLIX_API_KEY
          </code>{" "}
          or use{" "}
          <code className="rounded bg-slate-700/50 px-1 font-mono text-xs">
            --api-key
          </code>
          . For a custom API URL, use{" "}
          <code className="rounded bg-slate-700/50 px-1 font-mono text-xs">
            --url
          </code>{" "}
          or{" "}
          <code className="rounded bg-slate-700/50 px-1 font-mono text-xs">
            QUANTLIX_API_URL
          </code>
          .
        </p>
      </div>

      <div className="mt-12 space-y-12">
        {COMMANDS.map(({ category, commands }) => (
          <section key={category}>
            <h2 className="mb-6 text-xl font-medium text-slate-200">
              {category}
            </h2>
            <div className="space-y-8">
              {commands.map(({ cmd, opts, desc }) => (
                <div
                  key={cmd}
                  className="rounded-lg border border-slate-800 bg-slate-900/30 p-6"
                >
                  <div className="relative">
                    <CopyButton text={cmd} />
                    <pre className="overflow-x-auto font-mono text-sm text-slate-200">
                      {cmd}
                    </pre>
                  </div>
                  <p className="mt-3 text-sm text-slate-400">{desc}</p>
                  {opts.length > 0 && (
                    <div className="mt-3">
                      <p className="text-xs font-medium text-slate-500">
                        Options
                      </p>
                      <p className="mt-1 font-mono text-xs text-slate-400">
                        {opts.join(" · ")}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>

      <div className="mt-16 flex flex-wrap gap-4">
        <Link href="/docs">
          <span className="rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-2 text-sm text-slate-300 hover:bg-slate-700/50 hover:text-slate-200">
            Quickstart guide
          </span>
        </Link>
        <Link href="/dashboard">
          <span className="rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-2 text-sm text-slate-300 hover:bg-slate-700/50 hover:text-slate-200">
            Dashboard
          </span>
        </Link>
      </div>
    </main>
  );
}
