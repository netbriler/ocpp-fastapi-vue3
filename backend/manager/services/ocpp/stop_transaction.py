from manager.models.tasks.stop_transaction import StopTransactionTask
from charge_point_node.models.stop_transaction import StopTransactionEvent


async def process_stop_transaction(
        session,
        event: StopTransactionEvent
) -> StopTransactionTask:

    payload = event.payload

    return StopTransactionTask(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id,
        id_tag_info={}
    )
