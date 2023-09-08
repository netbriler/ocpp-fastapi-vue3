from ocpp.v16.enums import ChargePointStatus

from charge_point_node.models.heartbeat import HeartbeatEvent
from core.utils import get_utc_as_string
from manager.models.tasks.heartbeat import HeartbeatTask
from manager.services.charge_points import update_charge_point
from manager.views.charge_points import ChargePointUpdateStatusView


async def process_heartbeat(session, event: HeartbeatEvent) -> HeartbeatTask:
    # Do some logic here
    data = ChargePointUpdateStatusView(status=ChargePointStatus.available)
    await update_charge_point(session, event.charge_point_id, data=data)
    return HeartbeatTask(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id,
        current_time=get_utc_as_string()
    )
