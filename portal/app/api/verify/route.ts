import { NextRequest, NextResponse } from "next/server";
import { COOKIE_NAME } from "@/lib/api";
import { logError } from "@/lib/logger";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const token = searchParams.get("token");
  if (!token) {
    return NextResponse.json(
      { ok: false, detail: "Missing token" },
      { status: 400 }
    );
  }

  try {
    const res = await fetch(`${API_URL}/auth/verify?token=${encodeURIComponent(token)}`);
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      return NextResponse.json(
        { ok: false, detail: data.detail || "Verification failed" },
        { status: res.status }
      );
    }

    const response = NextResponse.json({ ok: true });
    response.cookies.set(COOKIE_NAME, data.api_key, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 30, // 30 days
      path: "/",
    });
    return response;
  } catch (e) {
    logError("verify", "API request failed", e);
    return NextResponse.json(
      { ok: false, detail: "Network error" },
      { status: 502 }
    );
  }
}
