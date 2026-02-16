import { NextRequest, NextResponse } from "next/server";
import { COOKIE_NAME } from "@/lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  const apiKey = request.cookies.get(COOKIE_NAME)?.value;
  if (!apiKey) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const days = searchParams.get("days") || "30";

  const res = await fetch(`${API_URL}/usage/metrics?days=${days}`, {
    headers: { "X-API-Key": apiKey },
  });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    return NextResponse.json(data, { status: res.status });
  }
  return NextResponse.json(data);
}
