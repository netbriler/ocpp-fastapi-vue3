from manager.models.tasks.meter_values import MeterValuesTask
from charge_point_node.models.meter_values import MeterValuesEvent


async def process_meter_values(
        session,
        event: MeterValuesEvent
) -> MeterValuesTask:

    payload = event.payload

    return MeterValuesTask(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id
    )
