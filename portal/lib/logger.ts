/**
 * Server-side error logger for portal API routes.
 * Logs to stdout (picked up by container/hosting logs).
 */
export function logError(route: string, message: string, err?: unknown): void {
  const errStr = err instanceof Error ? err.message : String(err);
  const stack = err instanceof Error ? err.stack : undefined;
  console.error(`[portal:${route}] ${message}`, errStr);
  if (stack) {
    console.error(stack);
  }
}
