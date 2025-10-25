import asyncio
import signal

from src.db import init_db, close_db
from src.workers.update_proposal import process_messages as process_proposal_messages
from src.middleware.logging import setup_logging

logger = setup_logging()
shutdown_event = asyncio.Event()


async def main():
    await init_db()
    logger.info("database_initialized", status="ok")

    # Start the SQS worker as a task
    worker_task = asyncio.create_task(process_proposal_messages(shutdown_event))

    # Wait until shutdown signal is set
    await shutdown_event.wait()

    # Cancel the worker gracefully
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

    await close_db()
    logger.info("database_closed", status="ok")


def handle_shutdown(*_):
    logger.info("shutdown_signal_received")
    shutdown_event.set()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    asyncio.run(main())
