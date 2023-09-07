import json

from ocpp.v201.enums import Action
from pydantic import BaseModel

from core.fields import ConnectionStatus
from core.settings import EVENTS_QUEUE_NAME, REGULAR_MESSAGE_PRIORITY


class BaseEvent(BaseModel):
    message_id: str | None = None
    charge_point_id: str
    action: ConnectionStatus | Action
    target_queue: str = EVENTS_QUEUE_NAME
    priority: int = REGULAR_MESSAGE_PRIORITY

    def __str__(self):
        return self.json()
