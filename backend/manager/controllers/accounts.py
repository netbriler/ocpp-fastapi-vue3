from typing import List

from fastapi import APIRouter, status

from manager.models import Account
from manager.services.accounts import list_accounts
from manager.views.accounts import AccountView

accounts_router = APIRouter(
    prefix="/accounts",
    tags=["accounts"]
)


@accounts_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[AccountView]
)
async def retrieve_accounts() -> List[Account]:
    return await list_accounts()
