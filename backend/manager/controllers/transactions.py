from typing import Tuple

from fastapi import APIRouter, status, Depends

from core.database import get_contextual_session
from manager.models import Account
from manager.services.accounts import get_account
from manager.services.transactions import build_transactions_query
from manager.utils import params_extractor, paginate
from manager.views.transactions import PaginatedTransactionsView


transaction_router = APIRouter(
    prefix="/{account_id}",
    tags=["transaction"]
)


@transaction_router.get(
    "/transactions",
    status_code=status.HTTP_200_OK
)
async def list_transactions(
        search: str = "",
        account: Account = Depends(get_account),
        params: Tuple = Depends(params_extractor)
) -> PaginatedTransactionsView:
    async with get_contextual_session() as session:
        items, pagination = await paginate(
            session,
            lambda: build_transactions_query(account, search),
            *params
        )
        await session.close()
        return PaginatedTransactionsView(
            items=[item[0] for item in items],
            pagination=pagination
        )
