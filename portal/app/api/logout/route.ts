import { NextRequest, NextResponse } from "next/server";

const COOKIE_NAME = "quantlix_api_key";

export async function POST(request: NextRequest) {
  const response = NextResponse.redirect(new URL("/", request.url), 303);
  response.cookies.delete(COOKIE_NAME);
  return response;
}
