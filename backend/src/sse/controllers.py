import asyncio

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from starlette.requests import Request

from manager.models import Account
from manager.services.accounts import get_account
from sse import sse_publisher
from sse.observer import Observer

stream_router = APIRouter(tags=["stream"])


async def event_generator(observer: Observer):
    delay = 0.5  # seconds

    while True:
        event = await observer.consume_event()
        if event is not None:
            yield event
        await asyncio.sleep(delay)


@stream_router.get('/{account_id}/stream')
async def stream(request: Request, account: Account = Depends(get_account)):
    observer = Observer(request, account)
    await observer.subscribe(sse_publisher)

    return EventSourceResponse(
        event_generator(observer)
    )
