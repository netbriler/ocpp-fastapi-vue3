from ocpp.v201.enums import Action

from charge_point_node.models.base import BaseEvent


class StatusNotificationEventEvent(BaseEvent):
    action: Action = Action.StatusNotification
