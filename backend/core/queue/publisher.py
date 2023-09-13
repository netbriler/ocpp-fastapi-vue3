import aio_pika

from core.queue import get_connection, get_channel, get_exchange


async def publish(data: str, to: str, priority=None) -> None:
    connection = await get_connection()
    channel = await get_channel(connection, to)
    exchange = await get_exchange(channel, to)

    await exchange.publish(
        aio_pika.Message(
            bytes(data, "utf-8"),
            content_type="json",
            priority=priority
        ),
        routing_key=to,
    )
