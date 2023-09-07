from charge_point_node.models.base import BaseEvent
from manager.models.tasks.status_notification import StatusNotificationTask


async def process_status_notification(event: BaseEvent) -> StatusNotificationTask:
    # Do some logic here

    return StatusNotificationTask(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id
    )
