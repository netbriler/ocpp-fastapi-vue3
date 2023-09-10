from manager.models.tasks.stop_transaction import StopTransactionTask
from manager.services.transactions import update_transaction
from manager.views.transactions import UpdateTransactionView
from charge_point_node.models.stop_transaction import StopTransactionEvent

async def process_stop_transaction(
        session,
        event: StopTransactionEvent
) -> StopTransactionTask:

    view = UpdateTransactionView(
        transaction_id=event.payload.transaction_id,
        meter_stop=event.payload.meter_stop
    )
    await update_transaction(session, event.payload.transaction_id, view)

    return StopTransactionTask(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id,
        id_tag_info={}
    )
