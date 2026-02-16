import { NextRequest, NextResponse } from "next/server";
import { COOKIE_NAME } from "@/lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  const apiKey = request.cookies.get(COOKIE_NAME)?.value;
  if (!apiKey) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  const res = await fetch(`${API_URL}/billing/create-portal-session`, {
    method: "POST",
    headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
  });
  const data = await res.json().catch(() => ({}));

  if (!res.ok || !data.url) {
    return NextResponse.redirect(new URL("/?error=portal", request.url));
  }
  return NextResponse.redirect(data.url);
}
