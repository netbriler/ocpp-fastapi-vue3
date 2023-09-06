from __future__ import annotations

import asyncio

from sse import publisher as pub
from sse.views import SSEvent

counter = []


class Observer(asyncio.Queue):
    # in order to prevent memory overflow
    max_events_count = 10

    def __init__(self, request, account, *args, **kwargs):
        super().__init__(*args, **kwargs, maxsize=self.max_events_count)
        self.request = request
        self.account = account

    async def subscribe(self, publisher: pub.Publisher) -> None:
        await publisher.add_observer(self)

    async def unsubscribe(self, publisher: pub.Publisher) -> None:
        await publisher.remove_observer(self)

    async def gain_event(self, event: SSEvent) -> None:
        await self.put(event.json())

    async def consume_event(self) -> str:
        return await self.get()
