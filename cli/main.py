"""
CLI — Typer-based Python CLI for Quantlix
Usage: quantlix deploy, quantlix run, quantlix status
"""
import json
import os
from pathlib import Path
from typing import Optional

# Load .env from project root so CLOUD_API_KEY is available
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parents[1] / ".env"  # QUANTLIX_API_KEY, QUANTLIX_API_URL
    load_dotenv(env_path)
except ImportError:
    pass

import typer
from rich.console import Console
from rich.table import Table

from sdk.quantlix import QuantlixCloudClient, DEFAULT_BASE_URL

app = typer.Typer(
    name="quantlix",
    help="Quantlix CLI — deploy models, run inference, check status",
)
console = Console()


def _get_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> QuantlixCloudClient:
    key = api_key or os.environ.get("QUANTLIX_API_KEY", "").strip() or os.environ.get("CLOUD_API_KEY", "").strip()
    if not key:
        console.print("[red]Error: API key required. Set QUANTLIX_API_KEY (or CLOUD_API_KEY) or use --api-key[/red]")
        raise typer.Exit(1)
    url = base_url or os.environ.get("QUANTLIX_API_URL", "").strip() or os.environ.get("CLOUD_API_URL", "").strip() or DEFAULT_BASE_URL
    return QuantlixCloudClient(api_key=key, base_url=url)


@app.command()
def signup(
    email: str = typer.Option(..., "--email", "-e", prompt="Email", help="Your email"),
    password: str = typer.Option(..., "--password", "-p", prompt="Password", hide_input=True, help="Password (min 12 chars, upper, lower, digit, special)"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """Create a new account. Verification email will be sent — click the link to get your API key."""
    url = base_url or os.environ.get("QUANTLIX_API_URL", "").strip() or DEFAULT_BASE_URL
    try:
        result = QuantlixCloudClient.signup(email=email, password=password, base_url=url)
        console.print("[green]Account created[/green]")
        console.print(f"  [bold]{result.message}[/bold]")
        console.print(f"  email: [bold]{result.email}[/bold]")
        console.print("\n[dim]Check your inbox and click the verification link. Then run:[/dim]")
        console.print("  [bold]quantlix verify <token>[/bold]  [dim]# or quantlix login[/dim]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def verify(
    token: str = typer.Argument(..., help="Verification token from the email link"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """Verify email and get API key. Use the token from the verification link."""
    url = base_url or os.environ.get("QUANTLIX_API_URL", "").strip() or DEFAULT_BASE_URL
    try:
        result = QuantlixCloudClient.verify_email(token=token, base_url=url)
        console.print("[green]Email verified[/green]")
        console.print(f"  user_id: [bold]{result.user_id}[/bold]")
        console.print(f"  api_key: [bold]{result.api_key}[/bold]")
        console.print("\n[dim]Set in .env or export:[/dim]")
        console.print(f"  [bold]QUANTLIX_API_KEY={result.api_key}[/bold]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def resend_verification(
    email: str = typer.Option(..., "--email", "-e", help="Email to resend verification to"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """Resend verification email."""
    url = base_url or os.environ.get("QUANTLIX_API_URL", "").strip() or DEFAULT_BASE_URL
    try:
        result = QuantlixCloudClient.resend_verification(email=email, base_url=url)
        console.print("[green]" + result.get("message", "Verification email sent.") + "[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def forgot_password(
    email: str = typer.Option(..., "--email", "-e", prompt="Email", help="Email to send reset link to"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """Request password reset. Check your inbox for the reset link."""
    url = base_url or os.environ.get("QUANTLIX_API_URL", "").strip() or DEFAULT_BASE_URL
    try:
        result = QuantlixCloudClient.forgot_password(email=email, base_url=url)
        console.print("[green]" + result.get("message", "If that email is registered, a reset link was sent.") + "[/green]")
        console.print("\n[dim]Then run: quantlix reset-password <token> --password <new-password>[/dim]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def reset_password(
    token: str = typer.Argument(..., help="Reset token from the email link"),
    password: str = typer.Option(..., "--password", "-p", prompt="New password", hide_input=True, help="New password"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """Reset password using token from the email link."""
    url = base_url or os.environ.get("QUANTLIX_API_URL", "").strip() or DEFAULT_BASE_URL
    try:
        result = QuantlixCloudClient.reset_password(token=token, new_password=password, base_url=url)
        console.print("[green]" + result.get("message", "Password reset successfully.") + "[/green]")
        console.print("\n[dim]You can now log in with: quantlix login[/dim]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("api-keys")
def api_keys(
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", envvar="QUANTLIX_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """List API keys for your account."""
    client = _get_client(api_key=api_key, base_url=base_url)
    try:
        keys = client.list_api_keys()
        if not keys:
            console.print("[dim]No API keys.[/dim]")
            return
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Created")
        for k in keys:
            table.add_row(k.id, k.name or "—", str(k.created_at))
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("create-api-key")
def create_api_key(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Name for the key"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", envvar="QUANTLIX_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """Create a new API key. The key is shown only once — save it."""
    client = _get_client(api_key=api_key, base_url=base_url)
    try:
        result = client.create_api_key(name=name)
        console.print("[green]API key created[/green]")
        console.print(f"  id: [bold]{result.id}[/bold]")
        console.print(f"  api_key: [bold]{result.api_key}[/bold]")
        console.print("\n[red]Save this key now — it won't be shown again.[/red]")
        console.print("\n[dim]Set in .env or export:[/dim]")
        console.print(f"  [bold]QUANTLIX_API_KEY={result.api_key}[/bold]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("revoke-api-key")
def revoke_api_key(
    key_id: str = typer.Argument(..., help="API key ID to revoke (from quantlix api-keys)"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", envvar="QUANTLIX_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """Revoke an API key. It will stop working immediately."""
    client = _get_client(api_key=api_key, base_url=base_url)
    try:
        result = client.revoke_api_key(key_id)
        console.print("[green]" + result.get("message", "API key revoked.") + "[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("rotate-api-key")
def rotate_api_key(
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", envvar="QUANTLIX_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """Create a new API key and revoke the current one. Update QUANTLIX_API_KEY with the new key."""
    client = _get_client(api_key=api_key, base_url=base_url)
    try:
        result = client.rotate_api_key()
        console.print("[green]API key rotated[/green]")
        console.print(f"  id: [bold]{result.id}[/bold]")
        console.print(f"  api_key: [bold]{result.api_key}[/bold]")
        console.print("\n[red]Update QUANTLIX_API_KEY — the old key no longer works.[/red]")
        console.print("\n[dim]Set in .env or export:[/dim]")
        console.print(f"  [bold]QUANTLIX_API_KEY={result.api_key}[/bold]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def login(
    email: str = typer.Option(..., "--email", "-e", prompt="Email", help="Your email"),
    password: str = typer.Option(..., "--password", "-p", prompt="Password", hide_input=True, help="Password"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """Log in. Returns API key — set QUANTLIX_API_KEY."""
    url = base_url or os.environ.get("QUANTLIX_API_URL", "").strip() or DEFAULT_BASE_URL
    try:
        result = QuantlixCloudClient.login(email=email, password=password, base_url=url)
        console.print("[green]Logged in[/green]")
        console.print(f"  user_id: [bold]{result.user_id}[/bold]")
        console.print(f"  api_key: [bold]{result.api_key}[/bold]")
        console.print("\n[dim]Set in .env or export:[/dim]")
        console.print(f"  [bold]QUANTLIX_API_KEY={result.api_key}[/bold]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def deploy(
    model_id: str = typer.Argument(..., help="Model identifier (e.g. my-llama-7b)"),
    model_path: Optional[str] = typer.Option(None, "--model-path", "-p", help="MinIO path to model files"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="JSON config (e.g. '{\"replicas\": 1}')"),
    gpu: bool = typer.Option(False, "--gpu", "-g", help="Deploy with GPU (Pro: 2h/month included, extra at €0.50/hr)"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", envvar="QUANTLIX_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """Deploy a model to the inference platform."""
    client = _get_client(api_key=api_key, base_url=base_url)
    config_dict = json.loads(config) if config else {}
    if gpu:
        config_dict["gpu"] = True
    try:
        result = client.deploy(model_id=model_id, model_path=model_path, config=config_dict)
        console.print(f"[green]Deployment queued[/green]")
        console.print(f"  deployment_id: [bold]{result.deployment_id}[/bold]")
        console.print(f"  status: {result.status}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def run(
    deployment_id: str = typer.Argument(..., help="Deployment ID to run inference on"),
    input_data: str = typer.Option(
        "{}",
        "--input",
        "-i",
        help="JSON input (e.g. '{\"prompt\": \"Hello\"}' or path to .json file)",
    ),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", envvar="QUANTLIX_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """Run inference on a deployed model."""
    client = _get_client(api_key=api_key, base_url=base_url)
    # Support file path or inline JSON
    if input_data.strip().startswith("{") or input_data.strip().startswith("["):
        parsed = json.loads(input_data)
    else:
        # Assume file path
        path = Path(input_data).expanduser()
        if not path.exists():
            console.print(f"[red]Error: File not found: {input_data}[/red]")
            console.print("Use inline JSON instead: [dim]quantlix run <id> -i '{{\"prompt\": \"Hello\"}}'[/dim]")
            raise typer.Exit(1)
        with open(path) as f:
            parsed = json.load(f)
    try:
        result = client.run(deployment_id=deployment_id, input_data=parsed)
        console.print(f"[green]Job queued[/green]")
        console.print(f"  job_id: [bold]{result.job_id}[/bold]")
        console.print(f"  status: {result.status}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status(
    resource_id: str = typer.Argument(..., help="Deployment or job ID"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", envvar="QUANTLIX_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """Get status of a deployment or job."""
    client = _get_client(api_key=api_key, base_url=base_url)
    try:
        result = client.status(resource_id=resource_id)
        table = Table(show_header=False)
        table.add_column("Field", style="dim")
        table.add_column("Value", style="")
        table.add_row("id", result.id)
        table.add_row("type", result.type)
        table.add_row("status", result.status)
        if result.created_at:
            table.add_row("created_at", str(result.created_at))
        if result.updated_at:
            table.add_row("updated_at", str(result.updated_at))
        if result.error_message:
            table.add_row("error_message", result.error_message)
        if result.tokens_used is not None:
            table.add_row("tokens_used", str(result.tokens_used))
        if result.compute_seconds is not None:
            table.add_row("compute_seconds", str(result.compute_seconds))
        if result.output_data:
            table.add_row("output_data", json.dumps(result.output_data, indent=2))
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def usage(
    start_date: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", envvar="QUANTLIX_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", envvar="QUANTLIX_API_URL"),
):
    """Get usage stats (tokens, compute seconds, job count)."""
    client = _get_client(api_key=api_key, base_url=base_url)
    from datetime import date
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    try:
        result = client.usage(start_date=start, end_date=end)
        table = Table(show_header=False)
        table.add_column("Field", style="dim")
        table.add_column("Value", style="")
        table.add_row("user_id", result.user_id)
        table.add_row("tokens_used", str(result.tokens_used))
        table.add_row("compute_seconds", f"{result.compute_seconds:.0f}s (CPU)")
        table.add_row("gpu_seconds", f"{result.gpu_seconds:.0f}s")
        table.add_row("job_count", str(result.job_count))
        if result.start_date:
            table.add_row("start_date", str(result.start_date))
        if result.end_date:
            table.add_row("end_date", str(result.end_date))
        if result.tokens_limit is not None:
            table.add_row("tokens_limit", str(result.tokens_limit))
        if result.compute_limit is not None:
            table.add_row("compute_limit", f"{result.compute_limit:.0f}s")
        if result.gpu_limit is not None:
            table.add_row("gpu_limit", f"{result.gpu_limit/3600:.1f}h")
        if result.gpu_seconds_overage is not None and result.gpu_seconds_overage > 0:
            table.add_row("gpu_overage", f"{result.gpu_seconds_overage:.0f}s (€0.50/hr)")
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
