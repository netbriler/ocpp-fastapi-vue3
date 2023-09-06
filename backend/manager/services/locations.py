from typing import List

from sqlalchemy import func, select, or_, delete
from sqlalchemy.sql import selectable

from manager.models import ChargePoint, Location
from manager.views.locations import CreateLocationView

criterias = lambda account_id: [
    Location.account_id == account_id,
    Location.is_active.is_(True)
]


async def list_simple_locations(session, account_id: str) -> List[Location]:
    query = select(Location)
    for criteria in criterias(account_id):
        query = query.where(criteria)
    result = await session.execute(query)
    return [i[0] for i in result.unique().fetchall()]


async def remove_location(session, location_id: str):
    query = delete(Location).where(Location.id == location_id)
    await session.execute(query)


async def create_location(session, account_id: str, data: CreateLocationView) -> Location:
    location = Location(account_id=account_id, **data.dict())
    session.add(location)
    return location


async def build_locations_query(account_id: str, search: str) -> selectable:
    charge_points_count = func.count(ChargePoint.id) \
        .label("charge_points_count")
    query = select(Location, charge_points_count) \
        .outerjoin(ChargePoint) \
        .order_by(Location.created_at.desc()) \
        .group_by(Location.id)
    for criteria in criterias(account_id):
        query = query.where(criteria)
    if search:
        query = query.where(or_(
            func.lower(Location.name).contains(func.lower(search)),
            func.lower(Location.city).contains(func.lower(search)),
            func.lower(Location.address1).contains(func.lower(search)))
        )
    return query
