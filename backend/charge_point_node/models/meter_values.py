from ocpp.v16.enums import Action

from charge_point_node.models.base import BaseEvent
from ocpp.v16.call import MeterValuesPayload


class MeterValuesEvent(BaseEvent):
    action: Action = Action.MeterValues
    payload: MeterValuesPayload
