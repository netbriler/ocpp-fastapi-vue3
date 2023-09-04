from __future__ import annotations

import asyncio
from typing import Dict

from loguru import logger
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import select, update, text, func, or_, String
from sqlalchemy.sql import selectable

import manager.models as models
from core.database import get_contextual_session
from manager.models import ChargePoint
from manager.views.charge_points import CreateChargPointView


async def build_charge_points_query(account: models.Account, search: str) -> selectable:
    criterias = [
        models.Location.account_id == account.id,
        models.Location.is_active.is_(True),
        ChargePoint.is_active.is_(True)
    ]
    query = select(ChargePoint).outerjoin(models.Location)
    for criteria in criterias:
        query = query.where(criteria)
    query = query.order_by(ChargePoint.updated_at.asc())
    if search:
        query = query.where(or_(
            func.lower(ChargePoint.id).contains(func.lower(search)),
            func.cast(ChargePoint.status, String).ilike(f"%{search}%"),
            func.lower(ChargePoint.model).contains(func.lower(search)),
            func.lower(models.Location.address1).contains(func.lower(search)))
        )
    return query


async def get_charge_point(session, charge_point_id) -> ChargePoint | None:
    result = await session.execute(select(ChargePoint).where(ChargePoint.id == charge_point_id))
    return result.scalars().first()


async def create_charge_point(session, data: CreateChargPointView):
    data.password = sha256.hash(data.password)
    charge_point = ChargePoint(**data.dict())
    session.add(charge_point)


async def update_charge_point(
        charge_point_id: str,
        data
) -> None:
    logger.info((f"Start process update charge point status "
                 f"(charge_point_id={charge_point_id}, data={data})"))
    async with get_contextual_session() as session:
        await session.execute(update(ChargePoint) \
                              .where(ChargePoint.id == charge_point_id) \
                              .values(**data.dict(exclude_unset=True)))
        await session.commit()


async def get_statuses_counts(session, account_id: str) -> Dict:
    """
    A dict with statuses and counts. Example:
    {'offline': 1, 'available': 0, 'reserved': 0, 'charging': 0}
    """
    query = "SELECT status, count(status) AS count FROM charge_points cp " \
            "JOIN locations l ON l.id = cp.location_id " \
            "WHERE l.account_id = '%s' " \
            "GROUP BY status;" % account_id

    result = await session.execute(text(query))
    data = result.fetchall()
    await asyncio.sleep(1)
    return {item.status.lower(): item.count for item in data}
