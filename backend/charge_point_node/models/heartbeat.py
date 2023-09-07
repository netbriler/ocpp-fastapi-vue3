from ocpp.v16.enums import Action
from ocpp.v16.call import HeartbeatPayload

from charge_point_node.models.base import BaseEvent


class HeartbeatEvent(BaseEvent):
    action: Action = Action.Heartbeat
    payload: HeartbeatPayload
