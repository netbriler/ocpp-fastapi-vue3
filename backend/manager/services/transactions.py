from __future__ import annotations

from sqlalchemy import update, select, or_, func, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import selectable

import manager.models as models
from manager.models import Transaction
from manager.views.transactions import CreateTransactionView, UpdateTransactionView


async def create_transaction(
        session: AsyncSession,
        data: CreateTransactionView
) -> Transaction:
    transaction = Transaction(**data.dict())
    session.add(transaction)
    return transaction


async def update_transaction(
        session: AsyncSession,
        transaction_id: int,
        data: UpdateTransactionView
) -> None:
    await session.execute(
        update(Transaction) \
            .where(Transaction.transaction_id == transaction_id) \
            .values(**data.dict())
    )


async def get_transaction(
        session: AsyncSession,
        transaction_id: int
) -> Transaction:
    result = await session \
        .execute(select(Transaction) \
                 .where(Transaction.transaction_id == transaction_id))
    return result.scalars().first()


async def build_transactions_query(account: models.Account, search: str) -> selectable:
    criterias = [
        models.Transaction.account_id == account.id,
    ]
    query = select(Transaction)
    for criteria in criterias:
        query = query.where(criteria)
    query = query.order_by(Transaction.transaction_id.desc())
    if search:
        query = query.where(or_(
            func.lower(Transaction.city).contains(func.lower(search)),
            func.lower(Transaction.address).contains(func.lower(search)),
            func.cast(Transaction.vehicle, String).ilike(f"{search}%"),
            func.cast(Transaction.charge_point, String).ilike(f"{search}%"),
        ))
    return query