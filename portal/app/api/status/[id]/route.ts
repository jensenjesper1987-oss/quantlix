import { NextRequest, NextResponse } from "next/server";
import { COOKIE_NAME } from "@/lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const apiKey = request.cookies.get(COOKIE_NAME)?.value;
  if (!apiKey) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  const { id } = await params;
  const res = await fetch(`${API_URL}/status/${id}`, {
    headers: { "X-API-Key": apiKey },
  });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    return NextResponse.json(data, { status: res.status });
  }
  return NextResponse.json(data);
}
