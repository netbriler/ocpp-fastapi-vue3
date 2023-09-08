from uuid import uuid4
import random
from manager.models.tasks.start_transaction import StartTransactionTask
from charge_point_node.models.start_transaction import StartTransactionEvent


async def process_start_transaction(
        session,
        event: StartTransactionEvent
) -> StartTransactionTask:

    payload = event.payload

    return StartTransactionTask(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id,
        transaction_id=random.randint(100, 1000),
        id_tag_info={}
    )
