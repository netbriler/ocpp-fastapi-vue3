from uuid import uuid4

from core import settings
from core.database import get_contextual_session
from manager.services.accounts import list_accounts
from manager.services.charge_points import create_charge_point, remove_charge_point
from manager.services.locations import create_location, remove_location
from manager.views.charge_points import CreateChargPointView
from manager.views.locations import CreateLocationView

charge_point_id = str(uuid4())
host = "localhost"
url = f"ws://{host}:{settings.WS_SERVER_PORT}/{charge_point_id}"


async def init_data(charge_point_id):
    async with get_contextual_session() as session:
        accounts = await list_accounts(session)
        account = accounts[0]
        location_view = CreateLocationView(
            name=str(uuid4()),
            city="Kyiv",
            address1="address"
        )
        location = await create_location(session, account.id, location_view)
        await session.commit()
        charge_point_view = CreateChargPointView(
            location_id=location.id,
            id=charge_point_id,
            manufacturer="manufacturer",
            serial_number=str(uuid4()),
            model="model"
        )
        charge_point = await create_charge_point(session, charge_point_view)
        await session.commit()
    return account, location, charge_point


async def clean_tables(account, location, charge_point):
    async with get_contextual_session() as session:
        await remove_charge_point(session, charge_point.id)
        await remove_location(session, location.id)
        await session.commit()


