"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export function Nav() {
  const [user, setUser] = useState<{ plan?: string } | null>(null);

  useEffect(() => {
    fetch("/api/me", { credentials: "include" })
      .then((r) => (r.ok ? r.json() : null))
      .then(setUser)
      .catch(() => setUser(null));
  }, []);

  const loggedIn = user !== null;

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-[#0b0f19]/95 backdrop-blur">
      <nav className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="flex items-center">
          <img
            src="/logo.svg"
            alt="Quantlix"
            className="h-9 w-auto"
          />
        </Link>
        <div className="flex items-center gap-6">
          <Link
            href="/docs"
            className="text-sm text-slate-400 hover:text-slate-200"
          >
            Docs
          </Link>
          <Link
            href="/pricing"
            className="text-sm text-slate-400 hover:text-slate-200"
          >
            Pricing
          </Link>
          <Link
            href="/dashboard"
            className="text-sm text-slate-400 hover:text-slate-200"
          >
            Dashboard
          </Link>
          {!loggedIn && (
            <Link
              href="/signup"
              className="text-sm text-slate-400 hover:text-slate-200"
            >
              Sign up
            </Link>
          )}
          {user?.plan === "free" && (
            <Link
              href="/pricing"
              className="rounded-full border border-amber-700/60 bg-amber-950/40 px-2 py-0.5 text-xs text-amber-400 hover:border-amber-600/60 hover:bg-amber-950/60"
            >
              Free plan
            </Link>
          )}
          {user?.plan === "starter" && (
            <span className="rounded-full border border-slate-600 bg-slate-800/50 px-2 py-0.5 text-xs text-slate-300">
              Starter
            </span>
          )}
          {loggedIn ? (
            <form action="/api/logout" method="post">
              <Button variant="outline" size="sm" type="submit">
                Sign out
              </Button>
            </form>
          ) : (
            <Link href="/login">
              <Button variant="outline" size="sm">
                Sign in
              </Button>
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
}
