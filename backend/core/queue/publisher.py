import aio_pika

from core.queue import get_connection, get_channel, get_exchange
from core.settings import TASKS_QUEUE_NAME, EVENTS_QUEUE_NAME, TASKS_EXCHANGE_NAME, EVENTS_EXCHANGE_NAME

async def publish(data: str, to: str, priority=None) -> None:
    exchange = None
    connection = await get_connection()
    channel = await get_channel(connection, to)
    if to == TASKS_QUEUE_NAME:
        exchange = await get_exchange(channel, TASKS_EXCHANGE_NAME)
    if to == EVENTS_QUEUE_NAME:
        exchange = await get_exchange(channel, EVENTS_EXCHANGE_NAME)
    if not exchange:
        raise Exception("Could not declare exchange.")

    await exchange.publish(
        aio_pika.Message(
            bytes(data, "utf-8"),
            content_type="json",
            priority=priority
        ),
        routing_key=to,
    )
