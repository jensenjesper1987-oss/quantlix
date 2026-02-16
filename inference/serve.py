#!/usr/bin/env python3
"""
Quantlix inference container — runs text generation with DistilGPT2.
Modes:
  - Job mode (K8s): JOB_ID, INPUT, REDIS_URL env → run inference, write result to Redis
  - Server mode (local): HTTP server for orchestrator to call when MOCK_K8S=true
"""
import json
import os
import time

# Job mode: run once and exit
def run_job_mode() -> None:
    job_id = os.environ.get("JOB_ID")
    input_str = os.environ.get("INPUT", "{}")
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    if not job_id:
        raise SystemExit("JOB_ID required in job mode")

    try:
        input_data = json.loads(input_str)
    except json.JSONDecodeError:
        input_data = {"prompt": input_str[:200]}

    prompt = input_data.get("prompt", input_data.get("text", "Hello"))
    if isinstance(prompt, list):
        prompt = prompt[0] if prompt else "Hello"

    start = time.perf_counter()
    result = run_inference(prompt)
    elapsed = time.perf_counter() - start

    output = {
        "output_data": {"generated": result["text"], "model": "qx-example"},
        "tokens_used": result.get("tokens_used", 50),
        "compute_seconds": round(elapsed, 2),
    }

    import redis
    r = redis.Redis.from_url(redis_url, decode_responses=True)
    r.setex(f"inference:result:{job_id}", 3600, json.dumps(output))
    print(f"Wrote result to Redis for job {job_id}")


def run_inference(prompt: str, max_new_tokens: int = 50) -> dict:
    """Run text generation. Returns {text, tokens_used}."""
    from transformers import pipeline
    generator = pipeline("text-generation", model="distilbert/distilgpt2")
    out = generator(prompt, max_new_tokens=max_new_tokens, do_sample=True, pad_token_id=50256)
    text = out[0]["generated_text"] if out else ""
    # Rough token count (4 chars ~ 1 token for English)
    tokens_used = len(text.split()) * 2  # approximate
    return {"text": text, "tokens_used": min(tokens_used, 999)}


# Server mode: HTTP API for local dev
def run_server_mode() -> None:
    import uvicorn
    from fastapi import FastAPI
    from pydantic import BaseModel

    class RunRequest(BaseModel):
        job_id: str
        input: dict

    app = FastAPI(title="Quantlix Inference")

    @app.on_event("startup")
    def load_model():
        run_inference("warmup")  # Preload model on startup

    @app.post("/run")
    def run(req: RunRequest) -> dict:
        prompt = req.input.get("prompt", req.input.get("text", "Hello"))
        if isinstance(prompt, list):
            prompt = prompt[0] if prompt else "Hello"
        start = time.perf_counter()
        result = run_inference(str(prompt)[:500])
        elapsed = time.perf_counter() - start
        return {
            "output_data": {"generated": result["text"], "model": "qx-example"},
            "tokens_used": result.get("tokens_used", 50),
            "compute_seconds": round(elapsed, 2),
        }

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    if os.environ.get("JOB_ID"):
        run_job_mode()
    else:
        run_server_mode()
