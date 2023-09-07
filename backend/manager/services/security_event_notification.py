from manager.models.tasks.security_event_notification import SecurityEventNotificationTask
from charge_point_node.models.security_event_notification import SecurityEventNotificationEvent


async def process_security_event_notification(
        event: SecurityEventNotificationEvent
) -> SecurityEventNotificationTask:
    # Do some logic here

    return SecurityEventNotificationTask(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id
    )
