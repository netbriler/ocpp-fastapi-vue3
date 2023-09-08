from copy import deepcopy
from functools import wraps
from typing import Callable, Union

from loguru import logger

from ocpp.v16.enums import Action, ChargePointStatus

from charge_point_node.models.base import BaseEvent
from charge_point_node.models.security_event_notification import SecurityEventNotificationEvent
from charge_point_node.models.status_notification import StatusNotificationEvent
from charge_point_node.models.boot_notification import BootNotificationEvent
from charge_point_node.models.heartbeat import HeartbeatEvent
from charge_point_node.models.on_connection import LostConnectionEvent
from charge_point_node.models.authorize import AuthorizeEvent
from charge_point_node.models.start_transaction import StartTransactionEvent
from core.database import get_contextual_session
from core.fields import ConnectionStatus
from core.queue.publisher import publish
from manager.services.ocpp.boot_notification import process_boot_notification
from manager.services.charge_points import update_charge_point
from manager.services.ocpp.heartbeat import process_heartbeat
from manager.services.ocpp.security_event_notification import process_security_event_notification
from manager.services.ocpp.start_transaction import process_start_transaction
from manager.services.ocpp.status_notification import process_status_notification
from manager.services.ocpp.authorize import process_authorize
from manager.views.charge_points import ChargePointUpdateStatusView
from sse import sse_publisher


def prepare_event(func) -> Callable:
    @wraps(func)
    async def wrapper(data):
        event = {
            ConnectionStatus.LOST_CONNECTION: LostConnectionEvent,
            Action.StatusNotification: StatusNotificationEvent,
            Action.BootNotification: BootNotificationEvent,
            Action.Heartbeat: HeartbeatEvent,
            Action.SecurityEventNotification: SecurityEventNotificationEvent,
            Action.Authorize: AuthorizeEvent,
            Action.StartTransaction: StartTransactionEvent
        }[data["action"]](**data)
        return await func(event)

    return wrapper


@prepare_event
@sse_publisher.publish
async def process_event(event: Union[
    LostConnectionEvent,
    StatusNotificationEvent,
    BootNotificationEvent,
    HeartbeatEvent,
    SecurityEventNotificationEvent,
    AuthorizeEvent,
    StartTransactionEvent
]) -> BaseEvent | None:
    logger.info(f"Got event from charge point node (event={event})")

    task = None

    async with get_contextual_session() as session:

        if event.action is Action.StartTransaction:
            task = await process_start_transaction(session, deepcopy(event))
        if event.action is Action.Authorize:
            task = await process_authorize(session, deepcopy(event))
        if event.action is Action.SecurityEventNotification:
            task = await process_security_event_notification(session, deepcopy(event))
        if event.action is Action.BootNotification:
            task = await process_boot_notification(session, deepcopy(event))
        if event.action is Action.StatusNotification:
            task = await process_status_notification(session, deepcopy(event))
        if event.action is Action.Heartbeat:
            task = await process_heartbeat(session, deepcopy(event))

        if event.action is ConnectionStatus.LOST_CONNECTION:
            data = ChargePointUpdateStatusView(status=ChargePointStatus.unavailable)
            await update_charge_point(session, charge_point_id=event.charge_point_id, data=data)

        if task:
            await publish(task.json(), to=task.target_queue, priority=task.priority)

        await session.commit()
        logger.info(f"Successfully completed process event={event}")

        return event
