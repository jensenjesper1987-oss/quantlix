import type {
  APIKeyInfo,
  AuthResult,
  CreateAPIKeyResult,
  DeployResult,
  RunResult,
  SignupResult,
  StatusResult,
  UsageResult,
} from "./types";

export const DEFAULT_BASE_URL = "http://localhost:8000";

export class QuantlixCloudClient {
  private apiKey: string;
  private baseUrl: string;

  constructor(apiKey: string, baseUrl: string = DEFAULT_BASE_URL) {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  private headers(): Record<string, string> {
    return {
      "Content-Type": "application/json",
      "X-API-Key": this.apiKey,
    };
  }

  /** Create account. Sends verification email; use verifyEmail() after clicking the link. */
  static async signup(
    email: string,
    password: string,
    baseUrl: string = DEFAULT_BASE_URL
  ): Promise<SignupResult> {
    const url = baseUrl.replace(/\/$/, "");
    const res = await fetch(`${url}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `Signup failed: ${res.status}`);
    }
    return res.json();
  }

  /** Verify email and get API key. Call with token from verification link. */
  static async verifyEmail(
    token: string,
    baseUrl: string = DEFAULT_BASE_URL
  ): Promise<AuthResult> {
    const url = baseUrl.replace(/\/$/, "");
    const res = await fetch(`${url}/auth/verify?token=${encodeURIComponent(token)}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `Verification failed: ${res.status}`);
    }
    return res.json();
  }

  /** Request password reset. Sends email with reset link. */
  static async forgotPassword(
    email: string,
    baseUrl: string = DEFAULT_BASE_URL
  ): Promise<{ message: string }> {
    const url = baseUrl.replace(/\/$/, "");
    const res = await fetch(`${url}/auth/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `Forgot password failed: ${res.status}`);
    }
    return res.json();
  }

  /** Reset password using token from email link. */
  static async resetPassword(
    token: string,
    newPassword: string,
    baseUrl: string = DEFAULT_BASE_URL
  ): Promise<{ message: string }> {
    const url = baseUrl.replace(/\/$/, "");
    const res = await fetch(`${url}/auth/reset-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, new_password: newPassword }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `Reset password failed: ${res.status}`);
    }
    return res.json();
  }

  /** Resend verification email. */
  static async resendVerification(
    email: string,
    baseUrl: string = DEFAULT_BASE_URL
  ): Promise<{ message: string }> {
    const url = baseUrl.replace(/\/$/, "");
    const res = await fetch(`${url}/auth/resend-verification`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `Resend failed: ${res.status}`);
    }
    return res.json();
  }

  /** Log in. Returns API key for X-API-Key header. */
  static async login(
    email: string,
    password: string,
    baseUrl: string = DEFAULT_BASE_URL
  ): Promise<AuthResult> {
    const url = baseUrl.replace(/\/$/, "");
    const res = await fetch(`${url}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `Login failed: ${res.status}`);
    }
    return res.json();
  }

  /** Deploy a model to the inference platform. */
  async deploy(
    modelId: string,
    options?: { modelPath?: string; config?: Record<string, unknown> }
  ): Promise<DeployResult> {
    const res = await fetch(`${this.baseUrl}/deploy`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({
        model_id: modelId,
        model_path: options?.modelPath ?? null,
        config: options?.config ?? {},
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `Deploy failed: ${res.status}`);
    }
    return res.json();
  }

  /** Run inference on a deployed model. */
  async run(
    deploymentId: string,
    input: Record<string, unknown> | unknown[]
  ): Promise<RunResult> {
    const res = await fetch(`${this.baseUrl}/run`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({
        deployment_id: deploymentId,
        input,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `Run failed: ${res.status}`);
    }
    return res.json();
  }

  /** List API keys for the current user. */
  async listAPIKeys(): Promise<APIKeyInfo[]> {
    const res = await fetch(`${this.baseUrl}/auth/api-keys`, {
      method: "GET",
      headers: this.headers(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `List API keys failed: ${res.status}`);
    }
    const data = await res.json();
    return data.api_keys;
  }

  /** Create a new API key. The key is shown only once. */
  async createAPIKey(name?: string): Promise<CreateAPIKeyResult> {
    const res = await fetch(`${this.baseUrl}/auth/api-keys`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify(name ? { name } : {}),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `Create API key failed: ${res.status}`);
    }
    return res.json();
  }

  /** Revoke an API key. */
  async revokeAPIKey(keyId: string): Promise<{ message: string }> {
    const res = await fetch(`${this.baseUrl}/auth/api-keys/${keyId}`, {
      method: "DELETE",
      headers: this.headers(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `Revoke API key failed: ${res.status}`);
    }
    return res.json();
  }

  /** Create a new API key and revoke the current one. Returns the new key. */
  async rotateAPIKey(): Promise<CreateAPIKeyResult> {
    const res = await fetch(`${this.baseUrl}/auth/api-keys/rotate`, {
      method: "POST",
      headers: this.headers(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `Rotate API key failed: ${res.status}`);
    }
    return res.json();
  }

  /** Get status of a deployment or job. */
  async status(resourceId: string): Promise<StatusResult> {
    const res = await fetch(`${this.baseUrl}/status/${resourceId}`, {
      method: "GET",
      headers: this.headers(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `Status failed: ${res.status}`);
    }
    return res.json();
  }

  /** Get usage stats for the authenticated user. */
  async usage(options?: {
    startDate?: string;
    endDate?: string;
  }): Promise<UsageResult> {
    const params = new URLSearchParams();
    if (options?.startDate) params.set("start_date", options.startDate);
    if (options?.endDate) params.set("end_date", options.endDate);
    const qs = params.toString();
    const url = qs ? `${this.baseUrl}/usage?${qs}` : `${this.baseUrl}/usage`;
    const res = await fetch(url, {
      method: "GET",
      headers: this.headers(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? `Usage failed: ${res.status}`);
    }
    return res.json();
  }
}
