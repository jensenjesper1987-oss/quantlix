"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [verificationLink, setVerificationLink] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    setVerificationLink(null);
    try {
      const res = await fetch("/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.detail || "Signup failed");
        return;
      }
      setSuccess(true);
      if (data.verification_link) setVerificationLink(data.verification_link);
    } catch {
      setError("Network error");
    } finally {
      setLoading(false);
    }
  }

  if (success) {
    return (
      <main className="mx-auto flex min-h-[60vh] max-w-sm items-center justify-center px-4">
        <div className="w-full space-y-6 text-center">
          <h1 className="text-2xl font-semibold text-slate-100">
            Check your inbox
          </h1>
          <p className="text-slate-400">
            We sent a verification link to <span className="text-slate-200">{email}</span>.
            Click the link to activate your account.
          </p>
          {verificationLink && (
            <div className="rounded-lg border border-slate-600 bg-slate-800/50 p-3 text-left">
              <p className="mb-2 text-xs text-slate-400">
                Email not arriving? Use this link:
              </p>
              <a
                href={verificationLink}
                className="break-all text-sm text-purple-400 hover:underline"
              >
                {verificationLink}
              </a>
            </div>
          )}
          <Link href="/login">
            <Button variant="outline" className="w-full">
              Go to sign in
            </Button>
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto flex min-h-[60vh] max-w-sm items-center justify-center px-4">
      <div className="w-full space-y-8">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-slate-100">Sign up</h1>
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
              minLength={12}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-slate-200 placeholder-slate-400 focus:border-slate-600 focus:outline-none focus:ring-1 focus:ring-slate-600"
            />
            <p className="mt-1 text-xs text-slate-500">
              Min 12 chars, uppercase, lowercase, digit, special character
            </p>
          </div>
          {error && (
            <p className="text-sm text-red-400">{error}</p>
          )}
          <Button
            type="submit"
            disabled={loading}
            variant="primary"
            className="w-full"
          >
            {loading ? "Creating account..." : "Sign up"}
          </Button>
        </form>

        <p className="text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link href="/login" className="text-slate-300 hover:text-slate-200">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  );
}
