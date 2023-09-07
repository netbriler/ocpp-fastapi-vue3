from __future__ import annotations

from ocpp.v201.enums import Action
from pydantic import BaseModel

import manager.services.charge_points as service
from charge_point_node.models.base import BaseEvent
from core.database import get_contextual_session
from core.fields import ConnectionStatus
from manager.views.charge_points import StatusCount


class ConnectionMetaData(BaseModel):
    count: StatusCount


class HearbeatMetadata(BaseModel):
    pass


class SSEventData(BaseModel):
    charge_point_id: str
    name: str
    meta: dict = {}


class SSEvent(BaseModel):
    data: SSEventData
    event: str = "message"


class Redactor:

    async def prepare_event(self, event: BaseEvent, account_id: str) -> SSEvent:
        data = SSEventData(
            charge_point_id=event.charge_point_id,
            name=event.action
        )
        # Note: there is a list ALLOWED_SERVER_SIDE_EVENTS in the settings
        if event.action in [ConnectionStatus.NEW_CONNECTION, ConnectionStatus.LOST_CONNECTION]:
            async with get_contextual_session() as session:
                data.meta = ConnectionMetaData(
                    count=StatusCount(**await service.get_statuses_counts(session, account_id))
                ).dict()
        if event.action in [Action.Heartbeat]:
            data.meta = HearbeatMetadata().dict()

        return SSEvent(data=data)
