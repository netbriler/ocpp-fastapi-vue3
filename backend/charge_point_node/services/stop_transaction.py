from loguru import logger
from ocpp.v16.call import StopTransactionPayload as CallStartStopTransactionPayload
from ocpp.v16.call_result import StopTransactionPayload as CallResultStopTransactionPayload
from ocpp.v16.enums import Action

from manager.models.tasks.stop_transaction import StopTransactionTask
from charge_point_node.models.stop_transaction import StopTransactionEvent
from charge_point_node.router import Router
from core.queue.publisher import publish

router = Router()


@router.on(Action.StopTransaction)
async def on_stop_transaction(
        message_id: str,
        charge_point_id: str,
        **kwargs
):
    logger.info(f"Start stop transaction "
                f"(charge_point_id={charge_point_id}, "
                f"message_id={message_id},"
                f"payload={kwargs}).")
    event = StopTransactionEvent(
        charge_point_id=charge_point_id,
        message_id=message_id,
        payload=CallStartStopTransactionPayload(**kwargs)
    )
    await publish(event.json(), to=event.target_queue, priority=event.priority)


@router.out(Action.StopTransaction)
async def respond_stop_transaction(task: StopTransactionTask) -> CallResultStopTransactionPayload:
    logger.info(f"Start respond stop transaction task={task}).")
    return CallResultStopTransactionPayload(
        id_tag_info=task.id_tag_info
    )
