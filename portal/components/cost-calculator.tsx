"use client";

import { useState } from "react";

// Rough estimates: ~50 tokens/request for typical inference, Free=100k tokens, Starter=500k, Pro=1M
const TOKENS_PER_REQUEST = 50;
const FREE_TOKENS = 100_000;
const STARTER_TOKENS = 500_000;
const STARTER_PRICE = 9;
const PRO_TOKENS = 1_000_000;
const PRO_PRICE = 19;

export function CostCalculator() {
  const [requestsPerDay, setRequestsPerDay] = useState(1000);

  const requestsPerMonth = requestsPerDay * 30;
  const tokensPerMonth = requestsPerMonth * TOKENS_PER_REQUEST;

  let estimatedCost = "€0";
  let plan = "Free";
  if (tokensPerMonth <= FREE_TOKENS) {
    estimatedCost = "€0";
    plan = "Free";
  } else if (tokensPerMonth <= STARTER_TOKENS) {
    estimatedCost = `€${STARTER_PRICE}`;
    plan = "Starter";
  } else if (tokensPerMonth <= PRO_TOKENS) {
    estimatedCost = `€${PRO_PRICE}`;
    plan = "Pro";
  } else {
    estimatedCost = "Custom";
    plan = "Enterprise";
  }

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-6">
      <h3 className="font-medium text-slate-200">Monthly spending estimate</h3>
      <p className="mt-1 text-sm text-slate-500">
        ~{TOKENS_PER_REQUEST} tokens per request
      </p>
      <div className="mt-4 flex items-center gap-3">
        <label htmlFor="requests" className="text-sm text-slate-400">
          Requests/day:
        </label>
        <input
          id="requests"
          type="number"
          min={1}
          max={100000}
          value={requestsPerDay}
          onChange={(e) =>
            setRequestsPerDay(Math.max(1, parseInt(e.target.value) || 1))
          }
          className="w-24 rounded border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-slate-200 focus:border-slate-600 focus:outline-none focus:ring-1 focus:ring-slate-600"
        />
      </div>
      <div className="mt-4 flex items-baseline gap-2">
        <span className="text-2xl font-semibold text-slate-100">
          {estimatedCost}
        </span>
        <span className="text-sm text-slate-500">/month ({plan})</span>
      </div>
      <p className="mt-1 text-xs text-slate-500">
        ~{(tokensPerMonth / 1000).toFixed(0)}k tokens/month
      </p>
    </div>
  );
}
