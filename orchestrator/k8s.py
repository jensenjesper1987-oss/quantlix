"""
Kubernetes client — Create inference jobs.
Shared namespace + labels for multi-tenancy.
Mock mode for local dev without K8s cluster.
"""
import asyncio
import json
from datetime import datetime

from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException

from orchestrator.config import settings

NAMESPACE = "quantlix"
JOB_LABELS = {"app": "inference", "managed-by": "quantlix"}


def _get_k8s_client() -> client.BatchV1Api | None:
    """Load K8s config. Returns None if not configured."""
    if settings.mock_k8s:
        return None
    try:
        if settings.kubeconfig:
            config.load_kube_config(config_file=settings.kubeconfig)
        else:
            config.load_incluster_config()
        return client.BatchV1Api()
    except ConfigException:
        return None


async def create_inference_job(
    job_id: str,
    deployment_id: str,
    user_id: str,
    model_id: str,
    input_data: dict,
    *,
    use_gpu: bool = False,
) -> str | None:
    """
    Create K8s Job for inference. Returns job name if created, None if mock/skipped.
    """
    k8s = _get_k8s_client()
    if not k8s:
        return None

    job_name = f"inference-{job_id[:8]}"
    labels = {
        **JOB_LABELS,
        "user": user_id[:8],
        "model": model_id[:32].replace(".", "-"),
        "job-id": job_id,
    }

    input_json = json.dumps(input_data)[:4096]  # Reasonable limit for env

    container = client.V1Container(
        name="inference",
        image=settings.inference_image,
        env=[
            client.V1EnvVar(name="JOB_ID", value=job_id),
            client.V1EnvVar(name="INPUT", value=input_json),
            client.V1EnvVar(name="REDIS_URL", value=settings.redis_url),
        ],
    )

    pod_spec = client.V1PodSpec(
        restart_policy="Never",
        containers=[container],
    )
    if use_gpu:
        pod_spec.node_selector = {"quantlix.com/gpu": "true"}
        pod_spec.tolerations = [
            client.V1Toleration(
                key="nvidia.com/gpu",
                operator="Equal",
                value="true",
                effect="NoSchedule",
            )
        ]
    pod_template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels=labels),
        spec=pod_spec,
    )

    job = client.V1Job(
        metadata=client.V1ObjectMeta(name=job_name, labels=labels),
        spec=client.V1JobSpec(
            ttl_seconds_after_finished=300,
            template=pod_template,
        ),
    )

    await asyncio.to_thread(
        k8s.create_namespaced_job,
        namespace=NAMESPACE,
        body=job,
    )
    return job_name


async def wait_for_job_completion(job_name: str, timeout_seconds: int = 300) -> tuple[bool, str | None]:
    """
    Poll job until complete or timeout. Returns (success, error_message).
    """
    k8s = _get_k8s_client()
    if not k8s:
        return True, None  # Mock: consider success

    start = datetime.now()
    while (datetime.now() - start).total_seconds() < timeout_seconds:
        job = await asyncio.to_thread(
            k8s.read_namespaced_job,
            name=job_name,
            namespace=NAMESPACE,
        )
        if job.status.succeeded:
            return True, None
        if job.status.failed:
            return False, "Job failed"
        await asyncio.sleep(2)
    return False, "Timeout"
