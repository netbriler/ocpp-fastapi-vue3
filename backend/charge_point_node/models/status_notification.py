from ocpp.v16.enums import Action
from ocpp.v16.call import StatusNotificationPayload

from charge_point_node.models.base import BaseEvent


class StatusNotificationEvent(BaseEvent):
    action: Action = Action.StatusNotification
    payload: StatusNotificationPayload
