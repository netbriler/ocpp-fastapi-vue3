from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel
from ocpp.v16.enums import ChargePointStatus

from manager.views import PaginationView
from manager.views.locations import SimpleLocation


class ChargePointUpdateStatusView(BaseModel):
    status: ChargePointStatus


class StatusCount(BaseModel):
    available: int = 0
    offline: int = 0
    reserved: int = 0
    charging: int = 0


class CreateChargPointView(BaseModel):
    location_id: str
    id: str
    manufacturer: str
    serial_number: str
    model: str
    password: str | None = None
    comment: str | None = None


class SimpleChargePoint(BaseModel):
    id: str
    status: ChargePointStatus
    model: str
    updated_at: datetime | None = None
    location: SimpleLocation

    class Config:
        orm_mode = True


class PaginatedChargePointsView(BaseModel):
    items: List[SimpleChargePoint]
    pagination: PaginationView
