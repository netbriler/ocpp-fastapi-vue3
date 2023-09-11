from datetime import datetime
from typing import List

from pydantic import BaseModel

from manager.views import PaginationView


class CreateTransactionView(BaseModel):
    city: str
    vehicle: str
    address: str
    meter_start: int
    charge_point: str
    account_id : str


class UpdateTransactionView(BaseModel):
    meter_stop: int


class Transaction(BaseModel):
    id: str
    city: str
    vehicle: str
    address: str
    meter_start: int
    meter_stop: int | None = None
    charge_point: str
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        orm_mode = True

class PaginatedTransactionsView(BaseModel):
    items: List[Transaction]
    pagination: PaginationView