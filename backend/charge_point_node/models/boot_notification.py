from ocpp.v16.enums import Action
from ocpp.v16.call import BootNotificationPayload

from charge_point_node.models.base import BaseEvent


class BootNotificationEvent(BaseEvent):
    action: Action = Action.BootNotification
    payload: BootNotificationPayload
