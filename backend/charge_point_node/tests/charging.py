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
    StopTransactionPayload as CallStopTransactionPayload,
    MeterValuesPayload as CallMeterValuesPayload
)
from ocpp.v16.call_result import (
    AuthorizePayload as CallResultAuthorizePayload,
    StartTransactionPayload as CallResultStartTransactionPayload,
    StopTransactionPayload as CallResultStopTransactionPayload,
)
from ocpp.v16.enums import Action

from charge_point_node.tests import init_data, charge_point_id, url, clean_tables
from core.database import get_contextual_session
from manager.services.transactions import get_transaction

id_tag: str | None = None
transaction_id: int | None = None

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


async def test_start_transaction(websocket, account, location, charge_point):
    global transaction_id
    global id_tag

    id_tag = str(uuid4()).split("-")[0]
    meter_start = 1000

    start_transaction_payload = dataclasses.asdict(CallStartTransactionPayload(
        connector_id=1,
        id_tag=id_tag,
        meter_start=meter_start,
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

    async with get_contextual_session() as session:
        transaction = await get_transaction(session, payload.transaction_id)
        assert transaction.account_id == account.id
        assert transaction.city == location.city
        assert transaction.address == location.address1
        assert transaction.charge_point == charge_point.id
        assert transaction.meter_start == meter_start
        assert not transaction.meter_stop


async def test_meter_values(websocket):
    meter_values_payload = dataclasses.asdict(CallMeterValuesPayload(
        connector_id=1,
        transaction_id=123,
        meter_value=[
            {
                "timestamp": arrow.get().isoformat(),
                "sampled_value": [
                    {"value": "4567.45"}
                ]
            }
        ]
    ))
    message_id = str(uuid4())
    await websocket.send(json.dumps([
        2,
        message_id,
        Action.MeterValues.value,
        snake_to_camel_case({k: v for k, v in meter_values_payload.items() if not v is None})
    ]))
    await asyncio.sleep(1)
    response = await websocket.recv()
    data = json.loads(response)
    assert data[0] == 3
    assert data[1] == message_id
    assert not data[2]


async def test_stop_transaction(websocket, account, location, charge_point):

    meter_stop = 1200
    stop_transaction_payload = dataclasses.asdict(CallStopTransactionPayload(
        meter_stop=meter_stop,
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

    async with get_contextual_session() as session:
        transaction = await get_transaction(session, transaction_id)
        assert transaction.account_id == account.id
        assert transaction.city == location.city
        assert transaction.address == location.address1
        assert transaction.charge_point == charge_point.id
        assert transaction.meter_stop == meter_stop
        assert transaction.meter_stop >= transaction.meter_start


async def test_charging():
    account, location, charge_point = await init_data(charge_point_id)

    async with websockets.connect(url) as websocket:
        await test_authorize(websocket)
        await asyncio.sleep(1)
        await test_start_transaction(websocket, account, location, charge_point)
        await asyncio.sleep(5)
        await test_meter_values(websocket)
        await asyncio.sleep(1)
        await test_stop_transaction(websocket, account, location, charge_point)
        await asyncio.sleep(5)

    await clean_tables(account, location, charge_point)

    print("\n\n --- SUCCESS ---")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_charging())