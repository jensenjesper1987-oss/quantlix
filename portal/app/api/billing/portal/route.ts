import { NextRequest, NextResponse } from "next/server";
import { COOKIE_NAME } from "@/lib/api";
import { logError } from "@/lib/logger";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.PORTAL_API_URL ||
  process.env.API_URL ||
  "https://api.quantlix.ai";

export async function POST(request: NextRequest) {
  const apiKey = request.cookies.get(COOKIE_NAME)?.value;
  if (!apiKey) {
    return NextResponse.redirect(new URL("/login", request.url), 303);
  }

  try {
    const res = await fetch(`${API_URL}/billing/create-portal-session`, {
      method: "POST",
      headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
    });
    const data = await res.json().catch(() => ({}));

    if (!res.ok || !data.url) {
      logError("billing-portal", `API error: ${res.status}`, data.detail || data);
      return NextResponse.redirect(new URL("/dashboard?error=portal", request.url), 303);
    }
    return NextResponse.redirect(data.url, 303);
  } catch (e) {
    logError("billing-portal", "API request failed", e);
    return NextResponse.redirect(new URL("/dashboard?error=portal", request.url), 303);
  }
}
