import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, email, company, description } = body;

    if (!name || !email || !company || !description) {
      return NextResponse.json(
        { detail: "All fields are required" },
        { status: 400 }
      );
    }

    // TODO: Send email, store in DB, or forward to CRM
    // For now, log and return success
    console.log("Enterprise contact:", { name, email, company, description });

    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json(
      { detail: "Failed to submit" },
      { status: 500 }
    );
  }
}
