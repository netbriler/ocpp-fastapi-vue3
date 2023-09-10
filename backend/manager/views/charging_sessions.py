from pydantic import BaseModel

from core.fields import SessionStatus


class CreateChargingSessionView(BaseModel):
    status: SessionStatus = SessionStatus.IN_PROGRESS
    charge_point_id: str