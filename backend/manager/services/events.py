from copy import deepcopy
from functools import wraps
from typing import Callable, Union

from loguru import logger

from ocpp.v16.enums import Action, ChargePointStatus

from charge_point_node.models.base import BaseEvent
from charge_point_node.models.status_notification import StatusNotificationEvent
from charge_point_node.models.boot_notification import BootNotificationEvent
from charge_point_node.models.heartbeat import HeartbeatEvent
from charge_point_node.models.on_connection import OnConnectionEvent, LostConnectionEvent
from core.database import get_contextual_session
from core.fields import ConnectionStatus
from core.queue.publisher import publish
from manager.services.boot_notification import process_boot_notification
from manager.services.charge_points import update_charge_point, update_connectors
from manager.services.heartbeat import process_heartbeat
from manager.services.status_notification import process_status_notification
from manager.views.charge_points import ChargePointUpdateStatusView
from sse import sse_publisher


def prepare_event(func) -> Callable:
    @wraps(func)
    async def wrapper(data):
        event = {
            ConnectionStatus.LOST_CONNECTION: LostConnectionEvent,
            Action.StatusNotification: StatusNotificationEvent,
            Action.BootNotification: BootNotificationEvent,
            Action.Heartbeat: HeartbeatEvent
        }[data["action"]](**data)
        return await func(event)

    return wrapper


@prepare_event
@sse_publisher.publish
async def process_event(event: Union[
    LostConnectionEvent,
    StatusNotificationEvent,
    BootNotificationEvent,
    HeartbeatEvent
]) -> BaseEvent | None:
    logger.info(f"Got event from charge point node (event={event})")

    payload = None
    task = None

    async with get_contextual_session() as session:

        if event.action is Action.BootNotification:
            task = await process_boot_notification(deepcopy(event))
        if event.action is Action.StatusNotification:
            task = await process_status_notification(deepcopy(event))
            await update_connectors(session, event)
            if event.payload.connector_id == 0:
                payload = ChargePointUpdateStatusView(status=event.payload.status)
        if event.action is Action.Heartbeat:
            task = await process_heartbeat(deepcopy(event))
            payload = ChargePointUpdateStatusView(status=ChargePointStatus.available)
        if event.action is ConnectionStatus.LOST_CONNECTION:
            payload = ChargePointUpdateStatusView(status=ChargePointStatus.unavailable)

        if payload:
            await update_charge_point(session, charge_point_id=event.charge_point_id, data=payload)
            logger.info(f"Completed process event={event}")
        if task:
            await publish(task.json(), to=task.target_queue, priority=task.priority)

        await session.commit()
        return event
