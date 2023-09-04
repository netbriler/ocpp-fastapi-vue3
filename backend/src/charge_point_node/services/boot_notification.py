from loguru import logger
from ocpp.v201.call_result import BootNotificationPayload
from ocpp.v201.enums import Action

from charge_point_node.models.boot_notification import BootNotificationEvent
from charge_point_node.router import Router
from core.queue.publisher import publish
from manager.models.tasks.boot_notification import BootNotificationTask

router = Router()


@router.on(Action.BootNotification)
async def on_boot_notification(
        message_id: str,
        charge_point_id: str,
        **kwargs
):
    logger.info(f"Start accept boot notification "
                f"(charge_point_id={charge_point_id}, "
                f"message_id={message_id}).")
    event = BootNotificationEvent(
        charge_point_id=charge_point_id,
        message_id=message_id
    )
    await publish(event.json(), to=event.target_queue, priority=event.priority)


@router.out(Action.BootNotification)
async def respond_boot_notification(task: BootNotificationTask) -> BootNotificationPayload:
    logger.info(f"Start respond boot notification task={task}).")
    return BootNotificationPayload(
        current_time=task.current_time,
        interval=task.interval,
        status=task.status
    )
