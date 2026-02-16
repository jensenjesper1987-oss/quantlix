"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [verificationLink, setVerificationLink] = useState<string | null>(null);

  async function handleResend() {
    if (!email) return;
    setResendLoading(true);
    setError("");
    setVerificationLink(null);
    try {
      const res = await fetch("/api/resend-verification", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.detail || "Resend failed");
        return;
      }
      if (data.verification_link) setVerificationLink(data.verification_link);
      setError("");
    } catch {
      setError("Network error");
    } finally {
      setResendLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.detail || "Login failed");
        setVerificationLink(null);
        return;
      }
      router.push("/dashboard");
      router.refresh();
    } catch {
      setError("Network error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-[60vh] max-w-sm items-center justify-center px-4">
      <div className="w-full space-y-8">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-slate-100">Sign in</h1>
          <p className="mt-1 text-slate-500">Quantlix</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-slate-400"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-slate-200 placeholder-slate-400 focus:border-slate-600 focus:outline-none focus:ring-1 focus:ring-slate-600"
            />
          </div>
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-slate-400"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-slate-200 placeholder-slate-400 focus:border-slate-600 focus:outline-none focus:ring-1 focus:ring-slate-600"
            />
          </div>
          {error && (
            <div className="space-y-2">
              <p className="text-sm text-red-400">{error}</p>
              {error.includes("Email not verified") && (
                <div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={resendLoading || !email}
                    onClick={handleResend}
                  >
                    {resendLoading ? "Sending..." : "Resend verification link"}
                  </Button>
                  {verificationLink && (
                    <div className="mt-2 rounded border border-slate-600 bg-slate-800/50 p-2 text-left">
                      <a
                        href={verificationLink}
                        className="break-all text-xs text-purple-400 hover:underline"
                      >
                        {verificationLink}
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          <Button
            type="submit"
            disabled={loading}
            variant="primary"
            className="w-full"
          >
            {loading ? "Signing in..." : "Sign in"}
          </Button>
        </form>

        <p className="text-center text-sm text-slate-500">
          Don&apos;t have an account?{" "}
          <Link href="/signup" className="text-slate-300 hover:text-slate-200">
            Sign up
          </Link>
          {" · "}
          <Link href="/" className="text-slate-400 hover:text-slate-300">
            Back
          </Link>
        </p>
      </div>
    </main>
  );
}
