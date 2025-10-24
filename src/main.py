import asyncio
import signal

from src.db import init_db, close_db
from src.worker import process_messages
from src.middleware import setup_logging

logger = setup_logging()
shutdown_event = asyncio.Event()

async def main():
    await init_db()
    logger.info("database_initialized", status="ok")

    try:
        await process_messages(shutdown_event)
    finally:
        await close_db()
        logger.info("database_closed", status="ok")

def handle_shutdown(*_):
    logger.info("shutdown_signal_received")
    shutdown_event.set()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    asyncio.run(main())
