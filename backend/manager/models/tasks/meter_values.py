
from ocpp.v16.enums import Action

from manager.models.tasks.base import BaseTask


class MeterValuesTask(BaseTask):
    action: Action = Action.MeterValues
