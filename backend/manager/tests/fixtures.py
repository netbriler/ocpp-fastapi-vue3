import asyncio
import random

import arrow
from faker import Faker
from faker.exceptions import UniquenessException
from sqlalchemy import select

from core.database import get_contextual_session
from manager.models import Location, Account, ChargePoint
from manager.services.charge_points import create_charge_point
from manager.services.locations import create_location
from manager.services.transactions import create_transaction
from manager.views.charge_points import CreateChargPointView
from manager.views.locations import CreateLocationView
from manager.views.transactions import CreateTransactionView


async def list_all_locations():
    async with get_contextual_session() as session:
        query = select(Location)
        result = await session.execute(query)
        return [i[0] for i in result.unique().fetchmany()]


async def list_all_accounts():
    async with get_contextual_session() as session:
        query = select(Account)
        result = await session.execute(query)
        return [i[0] for i in result.unique().fetchmany()]


async def list_all_charge_points():
    async with get_contextual_session() as session:
        query = select(ChargePoint)
        result = await session.execute(query)
        return [i[0] for i in result.unique().fetchmany()]


async def create_dummy_locations(count):
    accounts = await list_all_accounts()
    accounts = [acc.id for acc in accounts]
    Faker.seed(0)
    fake = Faker()
    data = {
        "name": lambda: fake.unique.word(),
        "city": lambda: fake.city(),
        "address1": lambda: fake.unique.street_address(),
        "comment": lambda: fake.text(max_nb_chars=30)
    }
    async with get_contextual_session() as session:
        for i in range(count):
            try:
                view = CreateLocationView(**{k: v() for k, v in data.items()})
            except UniquenessException:
                continue
            await create_location(session, random.choice(accounts), view)
            await session.commit()


async def create_dummy_charge_points(count):
    locations = await list_all_locations()
    locations = [loc.id for loc in locations]
    Faker.seed(0)
    fake = Faker()
    data = {
        "location_id": lambda: random.choice(locations),
        "id": lambda: fake.unique.bothify(text='????-########', letters='ABCDE'),
        "manufacturer": lambda: fake.company(),
        "serial_number": lambda: fake.unique.bothify(text='????-###########', letters='QWER'),
        "model": lambda: fake.word(),
        "password": lambda: fake.unique.iana_id()
    }
    async with get_contextual_session() as session:
        for i in range(count):
            try:
                view = CreateChargPointView(**{k: v() for k, v in data.items()})
            except UniquenessException:
                continue
            await create_charge_point(session, view)
            await session.commit()


async def create_dummy_transactions(count):
    charge_points = await list_all_charge_points()
    locations = await list_all_locations()
    Faker.seed(0)
    fake = Faker()
    step = 50
    async with get_contextual_session() as session:
        prev_meter = 0
        for i in range(10, count*step, step):
            charge_point = random.choice(charge_points)
            location = random.choice(locations)
            data = {
                "city": location.city,
                "vehicle": fake.unique.bothify(text='????-###########', letters='ZYADER'),
                "address": location.address1,
                "meter_start": prev_meter,
                "charge_point": charge_point.id,
                "account_id": charge_point.location.account.id
            }
            prev_meter = i
            view = CreateTransactionView(**data)
            transaction = await create_transaction(session, view)
            transaction.meter_stop = i
            transaction.updated_at = arrow.utcnow().datetime.replace(tzinfo=None)
            session.add(transaction)
            await session.commit()



async def create_dummy_data(
        locations=100,
        charge_points=200,
        transactions=500
):
    await create_dummy_locations(locations),
    await create_dummy_charge_points(charge_points),
    await create_dummy_transactions(transactions)
