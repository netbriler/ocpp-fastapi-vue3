import json

from ocpp.v201.enums import Action
from pydantic import BaseModel

from core.fields import ConnectionStatus
from core.settings import EVENTS_EXCHANGE_NAME, REGULAR_MESSAGE_PRIORITY


class BaseEvent(BaseModel):
    message_id: str | None = None
    charge_point_id: str
    action: ConnectionStatus | Action
    exchange: str = EVENTS_EXCHANGE_NAME
    priority: int = REGULAR_MESSAGE_PRIORITY

    def __str__(self):
        return self.json()
