from core.fields import ConnectionStatus
from manager.models.tasks.base import BaseTask


class DisconnectTask(BaseTask):
    charge_point_id: str
    name: ConnectionStatus = ConnectionStatus.DISCONNECT

