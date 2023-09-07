from loguru import logger
from ocpp.v16.call import StatusNotificationPayload as CallStatusNotificationPayload
from ocpp.v16.call_result import StatusNotificationPayload as CallResultStatusNotificationPayload
from ocpp.v16.enums import Action

from charge_point_node.models.status_notification import StatusNotificationEvent
from charge_point_node.router import Router
from core.queue.publisher import publish
from manager.models.tasks.status_notification import StatusNotificationTask

router = Router()


@router.on(Action.StatusNotification)
async def on_status_notification(
        message_id: str,
        charge_point_id: str,
        **kwargs
):
    logger.info(f"Start accept status notification "
                f"(charge_point_id={charge_point_id}, "
                f"message_id={message_id},"
                f"payload={kwargs}).")
    event = StatusNotificationEvent(
        charge_point_id=charge_point_id,
        message_id=message_id,
        payload=CallStatusNotificationPayload(**kwargs)
    )
    await publish(event.json(), to=event.target_queue, priority=event.priority)


@router.out(Action.StatusNotification)
async def respond_status_notification(task: StatusNotificationTask) -> CallResultStatusNotificationPayload:
    logger.info(f"Start respond heartbeat task={task}).")
    return CallResultStatusNotificationPayload()
