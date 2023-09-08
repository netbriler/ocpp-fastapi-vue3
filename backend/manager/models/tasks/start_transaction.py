from typing import Dict

from ocpp.v16.enums import Action, RegistrationStatus

from manager.models.tasks.base import BaseTask


class StartTransactionTask(BaseTask):
    action: Action = Action.StartTransaction
    transaction_id: int
    id_tag_info: Dict
