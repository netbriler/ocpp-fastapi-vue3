from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

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