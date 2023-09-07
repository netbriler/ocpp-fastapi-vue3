from charge_point_node.models.base import BaseEvent
from core.fields import ConnectionStatus


class OnConnectionEvent(BaseEvent):
    action: ConnectionStatus = ConnectionStatus.NEW_CONNECTION


class LostConnectionEvent(BaseEvent):
    action: ConnectionStatus = ConnectionStatus.LOST_CONNECTION
