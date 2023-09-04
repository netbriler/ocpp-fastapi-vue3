import random

from faker import Faker
from faker.exceptions import UniquenessException
from sqlalchemy import select

from core.database import get_contextual_session
from manager.models import Location, Account
from manager.services.charge_points import create_charge_point
from manager.services.locations import create_location
from manager.views.charge_points import CreateChargPointView
from manager.views.locations import CreateLocationView


async def list_all_location_ids():
    async with get_contextual_session() as session:
        query = select(Location)
        result = await session.execute(query)
        return [i[0].id for i in result.unique().fetchmany()]


async def list_all_account_ids():
    async with get_contextual_session() as session:
        query = select(Account)
        result = await session.execute(query)
        return [i[0].id for i in result.unique().fetchmany()]


async def create_dummy_locations(count):
    accounts = await list_all_account_ids()
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
    locations = await list_all_location_ids()
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


async def create_dummy_data(locations=100, charge_points=200):
    await create_dummy_locations(locations)
    await create_dummy_charge_points(charge_points)
