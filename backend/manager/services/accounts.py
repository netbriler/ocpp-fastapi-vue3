from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session, get_contextual_session
from manager.exceptions import NotFound
from manager.models import Account
from manager.views.accounts import CreateAccountView


async def get_account(
        account_id: str,
        session: AsyncSession=Depends(get_session)
) -> Account:
    result = await session.execute(
        select(Account).where(Account.id == account_id)
    )
    account = result.scalars().first()
    if not account:
        result = await session.execute(
            select(Account)
        )
        account = result.scalars().first()
    if not account:
        raise NotFound(detail="Given account does not exist.")
    await session.close()
    return account


async def create_account(session, data: CreateAccountView) -> Account:
    account = Account(**data.dict())
    session.add(account)
    return account


async def list_accounts(session) -> List[Account]:
    query = select(Account).where(Account.is_active.is_(True))
    result = await session.execute(query)
    return [i[0] for i in result.unique().fetchall()]
