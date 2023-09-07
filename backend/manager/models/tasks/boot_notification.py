from ocpp.v16.enums import RegistrationStatus, Action

from manager.models.tasks.base import BaseTask


class BootNotificationTask(BaseTask):
    current_time: str
    interval: int
    status: RegistrationStatus
    action: Action = Action.BootNotification
