from typing import Dict

from ocpp.v16.enums import Action

from manager.models.tasks.base import BaseTask


class AuthorizeTask(BaseTask):
    id_tag_info: Dict
    action: Action = Action.Authorize
