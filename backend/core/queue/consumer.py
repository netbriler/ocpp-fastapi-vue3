import asyncio
import json
from typing import Dict

from aio_pika.abc import AbstractIncomingMessage

from core.queue import get_connection, get_channel, get_exchange
from core.settings import (
    EVENTS_QUEUE_NAME,
    TASKS_QUEUE_NAME,
    EVENTS_EXCHANGE_NAME,
    TASKS_EXCHANGE_NAME
)

async def start_consume(
        queue_name,
        on_message,
        prefetch_count=100,  # Maximum message count which will be processing at the same time.
) -> None:
    exchange = None
    connection = await get_connection()
    channel = await get_channel(connection, queue_name)

    if queue_name == TASKS_QUEUE_NAME:
        exchange = await get_exchange(channel, TASKS_EXCHANGE_NAME)
    if queue_name == EVENTS_QUEUE_NAME:
        exchange = await get_exchange(channel, EVENTS_EXCHANGE_NAME)
    if not exchange:
        raise Exception("Could not declare exchange.")

    await channel.set_qos(prefetch_count=prefetch_count)
    queue = await channel.declare_queue(queue_name, durable=True, exclusive=True)
    await queue.bind(exchange)

    async def parse_message(message: AbstractIncomingMessage) -> Dict:
        async with message.process():
            return await on_message(json.loads(message.body.decode()))

    await queue.consume(parse_message)

    try:
        # Wait until terminate
        await asyncio.Future()
    finally:
        await connection.close()
