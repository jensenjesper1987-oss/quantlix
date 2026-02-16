"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function PricingPage() {
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleEnterpriseSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const formData = new FormData(form);
    setLoading(true);
    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.get("name"),
          email: formData.get("email"),
          company: formData.get("company"),
          description: formData.get("description"),
        }),
      });
      if (res.ok) setSubmitted(true);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-16">
      <h1 className="text-3xl font-semibold text-slate-100">Pricing</h1>
      <p className="mt-4 text-slate-400">
        Transparent pricing. No hidden fees. Pay per usage.
      </p>

      <div className="mt-12 grid gap-6 md:grid-cols-4">
        <div className="rounded-lg border border-slate-800 bg-slate-900/30 p-6">
          <h2 className="font-medium text-slate-200">Free</h2>
          <p className="mt-2 text-2xl font-semibold text-slate-100">€0</p>
          <p className="mt-1 text-xs text-slate-500">Free queue: ~20s</p>
          <ul className="mt-4 space-y-2 text-sm text-slate-500">
            <li>100k tokens/month</li>
            <li>1 hour compute</li>
            <li>API access</li>
          </ul>
          <Link href="/signup" className="mt-6 block">
            <Button variant="secondary" className="w-full">
              Get started
            </Button>
          </Link>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900/30 p-6">
          <h2 className="font-medium text-slate-200">Starter</h2>
          <p className="mt-2 text-2xl font-semibold text-slate-100">€9/month</p>
          <p className="mt-1 text-xs text-[#10B981]">Priority queue</p>
          <ul className="mt-4 space-y-2 text-sm text-slate-500">
            <li>500k tokens/month</li>
            <li>5 hours compute</li>
            <li>Priority queue</li>
            <li>Email support</li>
          </ul>
          <form action="/api/billing/checkout" method="post" className="mt-6 block">
            <input type="hidden" name="plan" value="starter" />
            <Button variant="primary" className="w-full" type="submit">
              Upgrade to Starter
            </Button>
          </form>
        </div>

        <div className="rounded-lg border border-[#A855F7]/50 bg-slate-800/50 p-6">
          <h2 className="font-medium text-slate-200">Pro</h2>
          <p className="mt-2 text-2xl font-semibold text-slate-100">€19/month</p>
          <p className="mt-1 text-xs text-[#10B981]">Pro queue: instant</p>
          <ul className="mt-4 space-y-2 text-sm text-slate-500">
            <li>1M tokens/month</li>
            <li>10 hours CPU compute</li>
            <li>2 hours GPU/month included</li>
            <li>Extra GPU: €0.50/hour</li>
            <li>Priority support</li>
          </ul>
          <form action="/api/billing/checkout" method="post" className="mt-6 block">
            <input type="hidden" name="plan" value="pro" />
            <Button variant="primary" className="w-full" type="submit">
              Unlock faster deploy
            </Button>
          </form>
        </div>

        <div id="enterprise-form" className="rounded-lg border border-slate-800 bg-slate-900/30 p-6 scroll-mt-24">
          <h2 className="font-medium text-slate-200">Enterprise</h2>
          <p className="mt-2 text-2xl font-semibold text-slate-100">Custom</p>
          <ul className="mt-4 space-y-2 text-sm text-slate-500">
            <li>Unlimited usage</li>
            <li>GPU deployment</li>
            <li>Dedicated SLA</li>
            <li>Custom deployment</li>
          </ul>
          {submitted ? (
            <p className="mt-6 text-sm text-[#10B981]">
              Thanks! We&apos;ll be in touch.
            </p>
          ) : (
            <form
              onSubmit={handleEnterpriseSubmit}
              className="mt-6 space-y-3"
            >
              <input
                name="name"
                placeholder="Name"
                required
                className="w-full rounded border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:border-slate-600 focus:outline-none focus:ring-1 focus:ring-slate-600"
              />
              <input
                name="email"
                type="email"
                placeholder="Email"
                required
                className="w-full rounded border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:border-slate-600 focus:outline-none focus:ring-1 focus:ring-slate-600"
              />
              <input
                name="company"
                placeholder="Company"
                required
                className="w-full rounded border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:border-slate-600 focus:outline-none focus:ring-1 focus:ring-slate-600"
              />
              <textarea
                name="description"
                placeholder="Description"
                rows={3}
                required
                className="w-full rounded border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:border-slate-600 focus:outline-none focus:ring-1 focus:ring-slate-600"
              />
              <Button
                type="submit"
                variant="primary"
                className="w-full"
                disabled={loading}
              >
                {loading ? "Sending..." : "Contact us"}
              </Button>
            </form>
          )}
        </div>
      </div>

      <div className="mt-12 rounded-lg border border-[#A855F7]/30 bg-slate-900/50 p-6">
        <h2 className="font-medium text-slate-200">Deploy with GPU</h2>
        <p className="mt-2 text-sm text-slate-400">
          Run larger models and faster inference with NVIDIA GPU. Pro includes 2h GPU/month; extra hours at €0.50/hr. Enterprise: dedicated capacity.
        </p>
        <ul className="mt-3 space-y-1 text-sm text-slate-500">
          <li>• RTX 4000 Ada (20GB) — 2h/month included (Pro), then €0.50/hour</li>
          <li>• Enable via <code className="rounded bg-slate-800 px-1.5 py-0.5 text-slate-300">quantlix deploy --gpu</code> or dashboard</li>
          <li>• Enterprise: contact us for dedicated GPU capacity.</li>
        </ul>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link href="/dashboard">
            <Button variant="primary" size="sm">
              Unlock faster deploy
            </Button>
          </Link>
          <Link href="#enterprise-form" className="text-sm text-slate-400 hover:text-slate-300">
            Enterprise GPU →
          </Link>
        </div>
      </div>
    </main>
  );
}
