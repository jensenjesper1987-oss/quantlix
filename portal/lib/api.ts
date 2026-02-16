const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const COOKIE_NAME = "quantlix_api_key";

export async function fetchWithAuth(
  path: string,
  options: RequestInit & { cookie?: string } = {}
): Promise<Response> {
  const { cookie, ...init } = options;
  const apiKey = cookie ?? "";
  return fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...init.headers,
      "X-API-Key": apiKey,
      "Content-Type": "application/json",
    },
  });
}

export { COOKIE_NAME };
