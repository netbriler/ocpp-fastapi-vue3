from fastapi import APIRouter, Depends
from starlette import status

from manager.models import Account
from manager.services import get_counters
from manager.services.accounts import get_account
from manager.views import CountersView

common_router = APIRouter()


@common_router.get(
    "/{account_id}/counters",
    status_code=status.HTTP_200_OK,
    response_model=CountersView
)
async def retrieve_counters(
        account: Account = Depends(get_account)
):
    return await get_counters(account.id)
