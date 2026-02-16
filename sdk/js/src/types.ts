/** Result of deploy() */
export interface DeployResult {
  deployment_id: string;
  status: string;
  message: string;
}

/** Result of run() */
export interface RunResult {
  job_id: string;
  status: string;
  message: string;
}

/** Result of status() */
export interface StatusResult {
  id: string;
  type: string;
  status: string;
  created_at: string | null;
  updated_at: string | null;
  error_message: string | null;
  output_data: Record<string, unknown> | null;
  tokens_used: number | null;
  compute_seconds: number | null;
}

/** Result of usage() */
export interface UsageResult {
  user_id: string;
  tokens_used: number;
  compute_seconds: number;
  job_count: number;
  start_date: string | null;
  end_date: string | null;
  tokens_limit?: number | null;  // Monthly limit (0/unset = unlimited)
  compute_limit?: number | null;  // Monthly limit in seconds
}

/** Result of signup() — verification email sent */
export interface SignupResult {
  message: string;
  email: string;
}

/** Result of login() / verifyEmail() */
export interface AuthResult {
  api_key: string;
  user_id: string;
}

/** API key info (no secret) */
export interface APIKeyInfo {
  id: string;
  name: string | null;
  created_at: string;
}

/** Result of createAPIKey() / rotateAPIKey() */
export interface CreateAPIKeyResult {
  api_key: string;
  id: string;
  name: string | null;
}
