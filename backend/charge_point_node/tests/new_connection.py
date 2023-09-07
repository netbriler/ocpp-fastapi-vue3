import asyncio
import websockets
import json
from uuid import uuid4
import dataclasses
from http import HTTPStatus

import arrow
from websockets.exceptions import InvalidStatusCode
from ocpp.charge_point import snake_to_camel_case, camel_to_snake_case
from ocpp.v16.call import (
    BootNotificationPayload as CallBootNotificationPayload,
    StatusNotificationPayload as CallStatusNotificationPayload,
    SecurityEventNotificationPayload as CallSecurityEventNotificationPayload
)
from ocpp.v16.call_result import (
    BootNotificationPayload as CallResultBootNotificationPayload,
    HeartbeatPayload as CallResultHeartbeatPayload,
)
from ocpp.v16.enums import Action, ChargePointErrorCode, ChargePointStatus

from core import settings
from core.database import get_contextual_session
from manager.services.charge_points import get_charge_point
from manager.views.charge_points import ConnectorView

charge_point_id = "test"
host = "localhost"
url = f"ws://{host}:{settings.WS_SERVER_PORT}/{charge_point_id}"


async def test_unrecognized_charge_point():
    try:
        await websockets.connect(f"ws://{host}:{settings.WS_SERVER_PORT}/unrecognized")
        raise Exception
    except InvalidStatusCode as exc:
        assert HTTPStatus(exc.status_code) is HTTPStatus.UNAUTHORIZED


async def test_boot_notification(websocket):
    async with get_contextual_session() as session:
        charge_point = await get_charge_point(session, charge_point_id)
        status = charge_point.status

    boot_notification_payload = dataclasses.asdict(CallBootNotificationPayload(
        charge_point_model="test_model",
        charge_point_vendor="test_vendor",
    ))

    message_id = str(uuid4())
    await websocket.send(json.dumps([
        2,
        message_id,
        Action.BootNotification.value,
        snake_to_camel_case({k: v for k, v in boot_notification_payload.items() if not v is None})
    ]))

    response = await websocket.recv()
    data = json.loads(response)
    assert data[0] == 3
    assert data[1] == message_id
    CallResultBootNotificationPayload(**camel_to_snake_case(data[2]))
    async with get_contextual_session() as session:
        charge_point = await get_charge_point(session, charge_point_id)
        assert status == charge_point.status


async def test_status_notification(websocket):
    async with get_contextual_session() as session:
        charge_point = await get_charge_point(session, charge_point_id)
        connectors_length = len(charge_point.connectors.keys())

    status_notification_payload = dataclasses.asdict(CallStatusNotificationPayload(
        connector_id=0,
        error_code=ChargePointErrorCode.no_error,
        status=ChargePointStatus.available
    ))

    message_id = str(uuid4())
    await websocket.send(json.dumps([
        2,
        message_id,
        Action.StatusNotification.value,
        snake_to_camel_case({k: v for k, v in status_notification_payload.items() if not v is None})
    ]))
    response = await websocket.recv()
    data = json.loads(response)
    assert data[0] == 3
    assert data[1] == message_id
    assert not data[2]
    async with get_contextual_session() as session:
        charge_point = await get_charge_point(session, charge_point_id)
        assert charge_point.status is ChargePointStatus.available
        assert connectors_length == len(charge_point.connectors)

    status_notification_payload = dataclasses.asdict(CallStatusNotificationPayload(
        connector_id=1,
        error_code=ChargePointErrorCode.no_error,
        status=ChargePointStatus.reserved
    ))

    message_id = str(uuid4())
    await websocket.send(json.dumps([
        2,
        message_id,
        Action.StatusNotification.value,
        snake_to_camel_case({k: v for k, v in status_notification_payload.items() if not v is None})
    ]))
    await asyncio.sleep(2)
    response = await websocket.recv()
    data = json.loads(response)
    assert data[0] == 3
    assert data[1] == message_id
    assert not data[2]
    async with get_contextual_session() as session:
        charge_point = await get_charge_point(session, charge_point_id)
        assert len(charge_point.connectors) == 1
        connector = charge_point.connectors["1"]
        assert ConnectorView(**connector).dict() == ConnectorView(status=ChargePointStatus.reserved).dict()


async def test_heartbeat(websocket):

    message_id = str(uuid4())
    await websocket.send(json.dumps([
        2,
        message_id,
        Action.Heartbeat.value,
        {}
    ]))

    response = await websocket.recv()
    data = json.loads(response)
    assert data[0] == 3
    assert data[1] == message_id
    CallResultHeartbeatPayload(**camel_to_snake_case(data[2]))


async def test_security_notification_event(websocket):
    security_notification_payload = dataclasses.asdict(CallSecurityEventNotificationPayload(
        type="test_event",
        timestamp=arrow.get().isoformat(),
        tech_info="test_info"
    ))

    message_id = str(uuid4())
    await websocket.send(json.dumps([
        2,
        message_id,
        Action.SecurityEventNotification.value,
        snake_to_camel_case({k: v for k, v in security_notification_payload.items() if not v is None})
    ]))

    response = await websocket.recv()
    data = json.loads(response)
    assert data[0] == 3
    assert data[1] == message_id


async def test_new_connection():
    await test_unrecognized_charge_point()
    await asyncio.sleep(1)

    async with get_contextual_session() as session:
        charge_point = await get_charge_point(session, charge_point_id)
        if not charge_point:
            print(f"ERROR: Create charge point with id '{charge_point_id}', first.")
            return
        charge_point.connectors = {}
        charge_point.status = ChargePointStatus.unavailable.value
        session.add(charge_point)
        await session.commit()

    async with websockets.connect(url) as websocket:
        await test_boot_notification(websocket)
        await asyncio.sleep(1)
        await test_status_notification(websocket)
        await asyncio.sleep(1)
        await test_heartbeat(websocket)
        await asyncio.sleep(1)
        await test_security_notification_event(websocket)

        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_new_connection())