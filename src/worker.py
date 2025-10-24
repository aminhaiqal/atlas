import asyncio
import structlog

logger = structlog.get_logger(__name__)

async def process_messages(shutdown_event):
    logger.info("worker_started", msg="Listening for messages...")

    while not shutdown_event.is_set():
        # Future: replace with async SQS poller
        await asyncio.sleep(2)
        logger.info("heartbeat", message="Waiting for new messages...")

    logger.info("worker_stopped")
