import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const COOKIE_NAME = "quantlix_api_key";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const forwardedFor = request.headers.get("x-forwarded-for");
    const realIp = request.headers.get("x-real-ip");
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (forwardedFor) headers["X-Forwarded-For"] = forwardedFor;
    if (realIp) headers["X-Real-IP"] = realIp;
    const res = await fetch(`${API_URL}/auth/signup`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      return NextResponse.json(
        { detail: data.detail || "Signup failed" },
        { status: res.status }
      );
    }

    const response = NextResponse.json(data);
    // When email verification is disabled, API returns api_key — set cookie and user is logged in
    if (data.api_key) {
      response.cookies.set(COOKIE_NAME, data.api_key, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        maxAge: 60 * 60 * 24 * 30, // 30 days
        path: "/",
      });
    }
    return response;
  } catch (e) {
    return NextResponse.json(
      { detail: "Network error" },
      { status: 502 }
    );
  }
}
