import os
import asyncio
import json
import boto3
import structlog
from dotenv import load_dotenv

from src.tasks.denorm_proposal import serialized_proposal

logger = structlog.get_logger()

load_dotenv()

logger = structlog.get_logger()

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", 10))


sqs = boto3.client(
    "sqs",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


async def handle_message(message):
    """Process one message and return True if successful."""
    try:
        body = json.loads(message["Body"])
        proposal_id = body.get("proposal_id")

        if not proposal_id:
            logger.warning("invalid_message_body", message_id=message.get("MessageId"))
            return False

        logger.info(f"Received proposal_id: {proposal_id}")
        await serialized_proposal(proposal_id)
        return True

    except Exception as e:
        logger.exception("message_processing_failed", error=str(e))
        return False


async def poll_sqs_messages():
    """Receive messages from SQS via boto3 in a thread-safe way."""
    return await asyncio.to_thread(
        lambda: sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=MAX_CONCURRENT_TASKS,
            WaitTimeSeconds=10,
            VisibilityTimeout=60,
        )
    )


async def delete_sqs_messages(entries):
    """Delete processed messages."""
    if not entries:
        return
    await asyncio.to_thread(
        lambda: sqs.delete_message_batch(QueueUrl=SQS_QUEUE_URL, Entries=entries)
    )


async def process_messages(shutdown_event: asyncio.Event):
    """
    Continuously poll SQS and process messages concurrently,
    logging only failures.
    """
    while not shutdown_event.is_set():
        try:
            response = await poll_sqs_messages()
            messages = response.get("Messages", [])

            if not messages:
                await asyncio.sleep(1)
                continue

            # process concurrently
            results = await asyncio.gather(
                *[handle_message(m) for m in messages], return_exceptions=True
            )

            delete_entries = [
                {"Id": m["MessageId"], "ReceiptHandle": m["ReceiptHandle"]}
                for m, result in zip(messages, results)
                if result is True
            ]

            if delete_entries:
                await delete_sqs_messages(delete_entries)

        except Exception as e:
            logger.exception("sqs_loop_error", error=str(e))
