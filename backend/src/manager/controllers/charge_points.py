from typing import Tuple

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import delete

from core.database import get_contextual_session
from core.queue.publisher import publish
from manager.auth.charge_points import is_relevant_password
from manager.models import AuthData, Account, ChargePoint
from manager.models.tasks.connections import DisconnectTask
from manager.services.accounts import get_account
from manager.services.charge_points import (
    get_charge_point,
    get_statuses_counts, create_charge_point, build_charge_points_query
)
from manager.utils import acquire_lock, params_extractor, paginate
from manager.views.charge_points import StatusCount, PaginatedChargePointsView, CreateChargPointView

charge_points_router = APIRouter(
    tags=["charge_points"]
)


@charge_points_router.post(
    "/charge_points/{charge_point_id}",
    status_code=status.HTTP_200_OK
)
async def authenticate(charge_point_id: str, data: AuthData):
    async with get_contextual_session() as session:
        charge_point = await get_charge_point(session, charge_point_id)
        if not charge_point \
                or not await is_relevant_password(
            data.password,
            charge_point.password
        ):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)


@charge_points_router.get(
    "/{account_id}/charge_points",
    status_code=status.HTTP_200_OK
)
async def list_charge_points(
        search: str = "",
        account: Account = Depends(get_account),
        params: Tuple = Depends(params_extractor)
) -> PaginatedChargePointsView:
    async with get_contextual_session() as session:
        items, pagination = await paginate(
            session,
            lambda: build_charge_points_query(account, search),
            *params
        )
        return PaginatedChargePointsView(items=[item[0] for item in items], pagination=pagination)


@charge_points_router.post(
    "/{account_id}/charge_points",
    status_code=status.HTTP_201_CREATED,
)
async def add_charge_point(
        data: CreateChargPointView,
        account: Account = Depends(get_account)
):
    async with get_contextual_session() as session:
        await create_charge_point(session, data)
        await session.commit()


@charge_points_router.get(
    "/{account_id}/charge_points/counters",
    status_code=status.HTTP_200_OK,
    response_model=StatusCount
)
async def get_counters(account: Account = Depends(get_account)):
    async with get_contextual_session() as session:
        return await get_statuses_counts(session, account.id)


@charge_points_router.patch(
    "/{account_id}/charge_points/{charge_point_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def disconnect(charge_point_id: str):
    await acquire_lock(charge_point_id)
    task = DisconnectTask(charge_point_id=charge_point_id)
    await publish(task.json(), to=task.target_queue)


@charge_points_router.delete(
    "/{account_id}/charge_points/{charge_point_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_charge_point(
        charge_point_id: str,
        account: Account = Depends(get_account),
):
    async with get_contextual_session() as session:
        query = delete(ChargePoint) \
            .where(ChargePoint.id == charge_point_id)
        await session.execute(query)
        await session.commit()