import asyncio
from http import HTTPStatus
from traceback import format_exc

import websockets
from loguru import logger
from ocpp.exceptions import NotSupportedError, FormatViolationError, ProtocolError, \
    PropertyConstraintViolationError
from ocpp.messages import unpack
from websockets.datastructures import Headers
from websockets.exceptions import InvalidHandshake

from charge_point_node.models.on_connection import LostConnectionEvent
from charge_point_node.protocols import OCPPWebSocketServerProtocol, api_client
from charge_point_node.router import Router
from charge_point_node.tasks import process_task
from core.queue.consumer import start_consume
from core.queue.publisher import publish
from core.settings import WS_SERVER_PORT, TASKS_EXCHANGE_NAME

background_tasks = set()
router = Router()


async def watch(connection: OCPPWebSocketServerProtocol):
    while True:

        try:
            raw_msg = await connection.recv()
        except Exception:
            break

        try:
            msg = unpack(raw_msg)
        except (FormatViolationError, ProtocolError, PropertyConstraintViolationError) as exc:
            logger.error("Could not parse message (message=%r, details=%r)" % (raw_msg, format_exc()))
            await connection.send({"code": "validation_failed", "details": exc.description})
            continue
        try:
            await router.handle_on(connection, msg)
        except NotSupportedError:
            logger.error("Caught error during call handling (details=%r)" % format_exc())
            continue
        except Exception as error:
            logger.error("Caught error during call handling (details=%r)" % format_exc())
            response = msg.create_call_error(error).to_json()
            await connection.send(response)


async def on_connect(connection, path: str):
    charge_point_id = path.split("/")[-1].strip("/")
    if not charge_point_id:
        charge_point_id = f'No-id-provided-{id(connection)}'
    connection.charge_point_id = charge_point_id
    logger.info(f"New charge point connected (charge_point_id={charge_point_id})")

    response = await api_client.post(f"/charge_points/{charge_point_id}")
    response_status = HTTPStatus(response.status_code)

    if not response_status is HTTPStatus.OK:
        connection.write_http_response(response_status, Headers())
        logger.info(f"Could not validate charge point (charge_point_id={charge_point_id})")
        raise InvalidHandshake

    await watch(connection)

    logger.info(f"Closed connection (charge_point_id={charge_point_id})")
    event = LostConnectionEvent(charge_point_id=charge_point_id)
    await publish(event.json(), to=event.exchange, priority=event.priority)


async def main():
    server = await websockets.serve(
        on_connect, "0.0.0.0", WS_SERVER_PORT, subprotocols=["ocpp1.6"]
    )
    # Save a reference to the result of this function, to avoid a task disappearing mid-execution.
    # The event loop only keeps weak references to tasks.
    task = asyncio.create_task(
        start_consume(
            TASKS_EXCHANGE_NAME,
            on_message=lambda data: process_task(data, server)
        )
    )
    background_tasks.add(task)

    await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
