import asyncio
import json
from typing import Dict

from aio_pika.abc import AbstractIncomingMessage

from core.queue import get_connection, get_channel, get_exchange


async def start_consume(
        exchange_name,
        on_message,
        prefetch_count=100,  # Maximum message count which will be processing at the same time.
) -> None:
    connection = await get_connection()
    channel = await get_channel(connection, exchange_name)
    exchange = await get_exchange(channel, exchange_name)

    await channel.set_qos(prefetch_count=prefetch_count)
    queue = await channel.declare_queue(exclusive=True)
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
