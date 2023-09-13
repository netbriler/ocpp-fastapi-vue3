from loguru import logger
from ocpp.v16.call import MeterValuesPayload as CallMeterValuesPayload
from ocpp.v16.call_result import MeterValuesPayload as CallResultMeterValuesPayload
from ocpp.v16.enums import Action

from manager.models.tasks.meter_values import MeterValuesTask
from charge_point_node.models.meter_values import MeterValuesEvent
from charge_point_node.router import Router
from core.queue.publisher import publish

router = Router()


@router.on(Action.MeterValues)
async def on_meter_values(
        message_id: str,
        charge_point_id: str,
        **kwargs
):
    logger.info(f"Start handle meter values "
                f"(charge_point_id={charge_point_id}, "
                f"message_id={message_id},"
                f"payload={kwargs}).")
    event = MeterValuesEvent(
        charge_point_id=charge_point_id,
        message_id=message_id,
        payload=CallMeterValuesPayload(**kwargs)
    )
    await publish(event.json(), to=event.exchange, priority=event.priority)


@router.out(Action.MeterValues)
async def respond_meter_values(task: MeterValuesTask) -> CallResultMeterValuesPayload:
    logger.info(f"Start respond meter values task={task}).")
    return CallResultMeterValuesPayload()
