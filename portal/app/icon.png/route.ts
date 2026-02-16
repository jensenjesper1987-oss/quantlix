import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  const filePath = path.join(process.cwd(), "app/public/icon.png");
  try {
    const buffer = await fs.promises.readFile(filePath);
    return new NextResponse(buffer, {
      headers: { "Content-Type": "image/png" },
    });
  } catch {
    return new NextResponse(null, { status: 404 });
  }
}
