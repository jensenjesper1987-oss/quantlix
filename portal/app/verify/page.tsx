"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";

function VerifyContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setError("Missing verification token. Check your email for the full link.");
      return;
    }

    fetch(`/api/verify?token=${encodeURIComponent(token)}`)
      .then((res) => res.json().catch(() => ({})))
      .then((data) => {
        if (data.ok) {
          setStatus("success");
          router.push("/dashboard");
          router.refresh();
        } else {
          setStatus("error");
          setError(data.detail || "Verification failed. The link may have expired.");
        }
      })
      .catch(() => {
        setStatus("error");
        setError("Network error. Please try again.");
      });
  }, [token, router]);

  return (
    <main className="mx-auto flex min-h-[60vh] max-w-sm items-center justify-center px-4">
      <div className="w-full space-y-8 text-center">
        <h1 className="text-2xl font-semibold text-slate-100">
          {status === "loading" && "Verifying your email…"}
          {status === "success" && "Email verified!"}
          {status === "error" && "Verification failed"}
        </h1>

        {status === "loading" && (
          <div className="flex justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-600 border-t-purple-500" />
          </div>
        )}

        {status === "success" && (
          <p className="text-slate-400">
            Redirecting you to the dashboard…
          </p>
        )}

        {status === "error" && (
          <div className="space-y-6">
            <p className="text-slate-400">{error}</p>
            <div className="flex flex-col gap-3">
              <Link href="/login">
                <Button variant="primary" className="w-full">
                  Go to sign in
                </Button>
              </Link>
              <Link href="/signup">
                <Button variant="outline" className="w-full">
                  Create account
                </Button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

export default function VerifyPage() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto flex min-h-[60vh] max-w-sm items-center justify-center px-4">
          <div className="w-full space-y-8 text-center">
            <h1 className="text-2xl font-semibold text-slate-100">
              Verifying your email…
            </h1>
            <div className="flex justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-600 border-t-purple-500" />
            </div>
          </div>
        </main>
      }
    >
      <VerifyContent />
    </Suspense>
  );
}
