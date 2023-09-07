from ocpp.v16.enums import Action

from manager.models.tasks.base import BaseTask


class SecurityEventNotificationTask(BaseTask):
    action: Action = Action.SecurityEventNotification
