"""Prometheus metrics for users, usage, and tiers."""
from prometheus_client import Gauge

# Users
quantlix_users_total = Gauge(
    "quantlix_users_total",
    "Total number of registered users",
)
quantlix_users_by_plan = Gauge(
    "quantlix_users_by_plan",
    "Number of users per plan/tier",
    ["plan"],
)
quantlix_users_verified = Gauge(
    "quantlix_users_verified",
    "Number of users with verified email",
)

# Usage (current month)
quantlix_usage_tokens_total = Gauge(
    "quantlix_usage_tokens_total",
    "Total tokens used across all users this month",
)
quantlix_usage_compute_seconds_total = Gauge(
    "quantlix_usage_compute_seconds_total",
    "Total CPU compute seconds across all users this month",
)
quantlix_usage_gpu_seconds_total = Gauge(
    "quantlix_usage_gpu_seconds_total",
    "Total GPU seconds across all users this month",
)
quantlix_usage_jobs_total = Gauge(
    "quantlix_usage_jobs_total",
    "Total inference jobs this month",
)
