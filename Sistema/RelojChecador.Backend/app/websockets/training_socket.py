import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.training_progress_store import training_progress_store

router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/training/{job_id}")
async def training_progress_websocket(websocket: WebSocket, job_id: str):
    """Envía al frontend el avance del entrenamiento por job_id."""
    await websocket.accept()
    last_version = -1

    try:
        await websocket.send_json(
            {
                "event_type": "training_progress",
                "job_id": job_id,
                "status": "waiting",
                "percent": 0,
                "step": "waiting",
                "message": "Esperando que inicie la captura/entrenamiento...",
                "version": 0,
                "extra": {},
            }
        )

        while True:
            state = training_progress_store.get(job_id)

            if state and int(state.get("version", 0)) != last_version:
                last_version = int(state.get("version", 0))
                await websocket.send_json(state)

                if state.get("status") in {"completed", "failed"}:
                    await asyncio.sleep(5)
                    break

            await asyncio.sleep(0.4)

    except WebSocketDisconnect:
        pass
