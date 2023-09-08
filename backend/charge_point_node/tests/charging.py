import asyncio

import arrow
import websockets
import json
from uuid import uuid4
import dataclasses

from ocpp.charge_point import snake_to_camel_case, camel_to_snake_case
from ocpp.v16.call import (
    AuthorizePayload as CallAuthorizePayload,
    StartTransactionPayload as CallStartTransactionPayload,
    StopTransactionPayload as CallStopTransactionPayload
)
from ocpp.v16.call_result import (
    AuthorizePayload as CallResultAuthorizePayload,
    StartTransactionPayload as CallResultStartTransactionPayload,
    StopTransactionPayload as CallResultStopTransactionPayload
)
from ocpp.v16.enums import Action

from core import settings
from core.database import get_contextual_session
from manager.views.charge_points import CreateChargPointView
from manager.views.locations import CreateLocationView
from manager.services.charge_points import create_charge_point, remove_charge_point
from manager.services.locations import create_location, remove_location
from manager.services.accounts import list_accounts


id_tag: str | None = None
transaction_id: int | None = None
charge_point_id = str(uuid4())
host = "localhost"
url = f"ws://{host}:{settings.WS_SERVER_PORT}/{charge_point_id}"


async def init_data():
    global account
    global location
    global charge_point

    async with get_contextual_session() as session:
        accounts = await list_accounts(session)
        location_view = CreateLocationView(
            name=str(uuid4()),
            city="Kyiv",
            address1="address"
        )
        location = await create_location(session, accounts[0].id, location_view)
        await session.commit()
        charge_point_view = CreateChargPointView(
            location_id=location.id,
            id=charge_point_id,
            manufacturer="manufacturer",
            serial_number=str(uuid4()),
            model="model"
        )
        await create_charge_point(session, charge_point_view)
        await session.commit()

async def clean_tables():
    async with get_contextual_session() as session:
        await remove_charge_point(session, charge_point_id)
        await remove_location(session, location.id)


async def test_authorize(websocket):

    authorize_payload = dataclasses.asdict(CallAuthorizePayload(
        id_tag=str(uuid4()).split("-")[0]
    ))

    message_id = str(uuid4())
    await websocket.send(json.dumps([
        2,
        message_id,
        Action.Authorize.value,
        snake_to_camel_case({k: v for k, v in authorize_payload.items() if not v is None})
    ]))
    await asyncio.sleep(1)
    response = await websocket.recv()
    data = json.loads(response)
    assert data[0] == 3
    assert data[1] == message_id
    CallResultAuthorizePayload(**camel_to_snake_case(data[2]))


async def test_start_transaction(websocket):
    global transaction_id
    global id_tag

    id_tag = str(uuid4()).split("-")[0]

    start_transaction_payload = dataclasses.asdict(CallStartTransactionPayload(
        connector_id=1,
        id_tag=id_tag,
        meter_start=1000,
        timestamp=arrow.get().isoformat()
    ))

    message_id = str(uuid4())
    await websocket.send(json.dumps([
        2,
        message_id,
        Action.StartTransaction.value,
        snake_to_camel_case({k: v for k, v in start_transaction_payload.items() if not v is None})
    ]))
    await asyncio.sleep(1)
    response = await websocket.recv()
    data = json.loads(response)
    assert data[0] == 3
    assert data[1] == message_id
    payload = CallResultStartTransactionPayload(**camel_to_snake_case(data[2]))
    transaction_id = payload.transaction_id


async def test_stop_transaction(websocket):

    stop_transaction_payload = dataclasses.asdict(CallStopTransactionPayload(
        meter_stop=1200,
        id_tag=id_tag,
        timestamp=arrow.get().isoformat(),
        transaction_id=transaction_id
    ))

    message_id = str(uuid4())
    await websocket.send(json.dumps([
        2,
        message_id,
        Action.StopTransaction.value,
        snake_to_camel_case({k: v for k, v in stop_transaction_payload.items() if not v is None})
    ]))
    await asyncio.sleep(1)
    response = await websocket.recv()
    data = json.loads(response)
    assert data[0] == 3
    assert data[1] == message_id
    CallResultStopTransactionPayload(**camel_to_snake_case(data[2]))


async def test_charging():
    await init_data()

    async with websockets.connect(url) as websocket:
        await test_authorize(websocket)
        await asyncio.sleep(1)
        await test_start_transaction(websocket)
        await asyncio.sleep(1)
        await test_stop_transaction(websocket)
        await asyncio.sleep(1)

    await clean_tables()

    print("\n\n --- SUCCESS ---")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_charging())