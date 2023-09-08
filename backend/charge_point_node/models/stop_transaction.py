from ocpp.v16.enums import Action

from charge_point_node.models.base import BaseEvent
from ocpp.v16.call import StopTransactionPayload


class StopTransactionEvent(BaseEvent):
    action: Action = Action.StopTransaction
    payload: StopTransactionPayload
