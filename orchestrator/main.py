"""
Orchestrator — Job scheduling, GPU node selection, queue management.
Consumes from Redis, creates K8s jobs, updates DB and UsageRecord.
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from prometheus_client import start_http_server

from orchestrator.worker import run_worker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan():
    start_http_server(9091)
    yield


async def main():
    async with lifespan():
        worker_task = asyncio.create_task(run_worker())
        try:
            await worker_task
        except asyncio.CancelledError:
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down")
