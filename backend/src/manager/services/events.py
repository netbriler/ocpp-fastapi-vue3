from copy import deepcopy
from functools import wraps
from typing import Callable

from loguru import logger
from ocpp.v201.enums import Action

import manager.services.charge_points as service
from charge_point_node.models.base import BaseEvent
from charge_point_node.models.boot_notification import BootNotificationEvent
from charge_point_node.models.heartbeat import HeartbeatEvent
from charge_point_node.models.on_connection import OnConnectionEvent, LostConnectionEvent
from core.fields import ActionName, ChargePointStatus
from core.queue.publisher import publish
from manager.services.boot_notification import process_boot_notification
from manager.services.charge_points import update_charge_point
from manager.services.heartbeat import process_heartbeat
from manager.utils import release_lock
from manager.views.charge_points import ChargePointUpdateStatusView
from sse import sse_publisher
from core.database import get_contextual_session


def prepare_event(func) -> Callable:
    @wraps(func)
    async def wrapper(data):
        event = {
            ActionName.NEW_CONNECTION: OnConnectionEvent,
            ActionName.LOST_CONNECTION: LostConnectionEvent,
            Action.BootNotification: BootNotificationEvent,
            Action.Heartbeat: HeartbeatEvent
        }[data["action"]](**data)
        return await func(event)

    return wrapper


@prepare_event
@sse_publisher.publish
async def process_event(event: BaseEvent) -> BaseEvent | None:
    logger.info(f"Got event from charge point node (event={event})")

    # Do nothing if the charge point was not recognized
    async with get_contextual_session() as session:
        if not await service.get_charge_point(
            session,
            event.charge_point_id
        ):
            return

    payload = None
    task = None

    if event.action is Action.BootNotification:
        task = await process_boot_notification(deepcopy(event))
    if event.action is Action.Heartbeat:
        task = await process_heartbeat(deepcopy(event))

    if event.action in [
        ActionName.NEW_CONNECTION,
        Action.Heartbeat,
        Action.BootNotification
    ]:
        payload = ChargePointUpdateStatusView(status=ChargePointStatus.AVAILABLE)
    if event.action is ActionName.LOST_CONNECTION:
        payload = ChargePointUpdateStatusView(status=ChargePointStatus.UNAVAILABLE)

    if payload:
        await update_charge_point(charge_point_id=event.charge_point_id, data=payload)
        logger.info(f"Completed process event={event}")
    if task:
        await publish(task.json(), to=task.target_queue, priority=task.priority)

    await release_lock(event.charge_point_id)
    return event
