from pydantic import BaseModel


class CreateTransactionView(BaseModel):
    city: str
    vehicle: str
    address: str
    meter_start: int
    charge_point: str
    account_id : str


class UpdateTransactionView(BaseModel):
    meter_stop: int