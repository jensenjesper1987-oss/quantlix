import { NextRequest, NextResponse } from "next/server";
import { COOKIE_NAME } from "@/lib/api";

// Use runtime env for server-side; NEXT_PUBLIC_ is baked in at build
const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.PORTAL_API_URL ||
  process.env.API_URL ||
  "https://api.quantlix.ai";

export async function POST(request: NextRequest) {
  const apiKey = request.cookies.get(COOKIE_NAME)?.value;
  if (!apiKey) {
    return NextResponse.redirect(new URL("/dashboard?error=checkout&code=auth", request.url), 303);
  }

  let plan = "pro";
  try {
    const formData = await request.formData();
    const p = formData.get("plan");
    if (p === "starter" || p === "pro") plan = p;
  } catch {
    // No form data, use default
  }

  let res: Response;
  let data: Record<string, unknown> = {};
  try {
    res = await fetch(`${API_URL}/billing/create-checkout-session?plan=${plan}`, {
      method: "POST",
      headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
    });
    data = (await res.json().catch(() => ({}))) as Record<string, unknown>;
  } catch (err) {
    // Network error, API unreachable
    console.error("[checkout] API request failed:", err);
    return NextResponse.redirect(new URL("/dashboard?error=checkout&code=network", request.url), 303);
  }

  if (!res.ok || !data.url) {
    const code = res.status === 401 ? "auth" : res.status === 503 ? "config" : "failed";
    return NextResponse.redirect(new URL(`/dashboard?error=checkout&code=${code}`, request.url), 303);
  }
  return NextResponse.redirect(data.url as string, 303);
}
