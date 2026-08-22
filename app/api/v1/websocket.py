import contextlib

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.events import subscribe_activity

router = APIRouter()


@router.websocket("/ws/activity")
async def activity_feed(websocket: WebSocket):
    await websocket.accept()
    pubsub = await subscribe_activity()
    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        pass
    finally:
        with contextlib.suppress(Exception):
            await pubsub.unsubscribe()
            await pubsub.close()
