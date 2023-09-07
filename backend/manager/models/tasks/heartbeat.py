from ocpp.v16.enums import Action

from manager.models.tasks.base import BaseTask


class HeartbeatTask(BaseTask):
    current_time: str
    action: Action = Action.Heartbeat
