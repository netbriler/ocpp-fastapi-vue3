from __future__ import annotations

from functools import wraps
from typing import List, Callable

from loguru import logger

import manager.services.charge_points as service
from charge_point_node.models.base import BaseEvent
from core import settings
from core.database import get_contextual_session
from sse import observer as obs
from sse.views import Redactor


class Publisher:
    observers: List[obs.Observer] = []

    def __init__(self, redactor: Redactor):
        self.redactor = redactor

    async def notify_observer(self, observer: obs.Observer, event: BaseEvent) -> None:
        event = await self.redactor.prepare_event(event, observer.account.id)
        if event:
            await observer.gain_event(event)

    async def ensure_observers(self) -> None:
        """
        Remove inactive observers from the 'observers' list.
        :return:
        """
        for observer in self.observers:
            if await observer.request.is_disconnected():
                self.observers.remove(observer)
                del observer

    def publish(self, func) -> Callable:
        """
        Publish new event for all observers in the list
        :param func:
        :return:
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            event = await func(*args, **kwargs)
            if event and event.action in settings.ALLOWED_SERVER_SENT_EVENTS:
                logger.info(f"Start sending sse (event={event})")
                async with get_contextual_session() as session:
                    charge_point = await service.get_charge_point(
                        session,
                        event.charge_point_id
                    )
                    if charge_point:
                        for observer in self.observers:
                            if charge_point.location.account.id == observer.account.id:
                                await self.notify_observer(observer, event)

        return wrapper

    async def add_observer(self, observer: obs.Observer) -> None:
        await self.ensure_observers()
        self.observers.append(observer)

    async def remove_observer(self, observer: obs.Observer) -> None:
        self.observers.remove(observer)
