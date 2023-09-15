from __future__ import annotations

from typing import Union

from ocpp.v16.enums import Action
from pydantic import BaseModel

import manager.services.charge_points as service
from charge_point_node.models.authorize import AuthorizeEvent
from charge_point_node.models.boot_notification import BootNotificationEvent
from charge_point_node.models.heartbeat import HeartbeatEvent
from charge_point_node.models.meter_values import MeterValuesEvent
from charge_point_node.models.on_connection import LostConnectionEvent
from charge_point_node.models.security_event_notification import SecurityEventNotificationEvent
from charge_point_node.models.start_transaction import StartTransactionEvent
from charge_point_node.models.status_notification import StatusNotificationEvent
from charge_point_node.models.stop_transaction import StopTransactionEvent
from core.database import get_contextual_session
from core.fields import ConnectionStatus
from manager.services.transactions import get_transaction
from manager.views.charge_points import StatusCount, SimpleChargePoint
from manager.views.transactions import Transaction


class ConnectionMetaData(BaseModel):
    count: StatusCount


class SSEventData(BaseModel):
    charge_point_id: str
    name: str
    meta: dict = {}


class SSEvent(BaseModel):
    data: SSEventData
    event: str = "message"


class Redactor:

    async def prepare_event(self,
        event: Union[
            LostConnectionEvent,
            StatusNotificationEvent,
            BootNotificationEvent,
            HeartbeatEvent,
            SecurityEventNotificationEvent,
            AuthorizeEvent,
            StartTransactionEvent,
            StopTransactionEvent,
            MeterValuesEvent
        ],
        account_id: str
    ) -> SSEvent:
        data = SSEventData(
            charge_point_id=event.charge_point_id,
            name=event.action
        )
        # Note: there is a list ALLOWED_SERVER_SIDE_EVENTS in the settings
        async with get_contextual_session() as session:
            if event.action in [ConnectionStatus.LOST_CONNECTION]:
                data.meta = ConnectionMetaData(
                    count=StatusCount(**await service.get_statuses_counts(session, account_id))
                ).dict()
            if event.action in [Action.StatusNotification]:
                charge_point = await service.get_charge_point(session, event.charge_point_id)
                data.meta = SimpleChargePoint.from_orm(charge_point).dict()
            if event.action in [Action.StopTransaction, Action.StartTransaction]:
                transaction = await get_transaction(session, event.transaction_id)
                data.meta = Transaction.from_orm(transaction).dict()

            await session.close()

        return SSEvent(data=data)
