from loguru import logger

from ocpp.v16.enums import AuthorizationStatus

from manager.models.tasks.start_transaction import StartTransactionTask
from manager.services.charge_points import get_charge_point
from manager.views.transactions import CreateTransactionView
from manager.services.transactions import create_transaction
from charge_point_node.models.start_transaction import StartTransactionEvent


async def process_start_transaction(
        session,
        event: StartTransactionEvent
) -> StartTransactionTask:
    logger.info(f"Start process StartTransaction (event={event})")
    charge_point = await get_charge_point(session, event.charge_point_id)
    view = CreateTransactionView(
        city=charge_point.location.city,
        address=charge_point.location.address1,
        vehicle=event.payload.id_tag,
        meter_start=event.payload.meter_start,
        charge_point=charge_point.id,
        account_id=charge_point.location.account.id
    )
    transaction = await create_transaction(session, view)
    await session.flush()

    return StartTransactionTask(
        message_id=event.message_id,
        charge_point_id=event.charge_point_id,
        transaction_id=transaction.transaction_id,
        id_tag_info={"status": AuthorizationStatus.accepted.value}
    )
