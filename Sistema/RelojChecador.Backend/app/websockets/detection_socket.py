from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database.session import SessionLocal
from app.services.config_service import ConfigService
from app.services.detection_service import detection_service
from app.services.device_service import DeviceService
from app.websockets.websocket_manager import websocket_manager

router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/detection")
async def detection_websocket(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    db = SessionLocal()
    pc_name: str | None = None

    try:
        while True:
            payload = await websocket.receive_json()
            message_type = payload.get("type")

            if message_type == "init":
                pc_name = payload.get("pc_name")
                if not pc_name:
                    await websocket_manager.send_json(
                        websocket,
                        {"event_type": "invalid_init", "message": "Debes enviar pc_name"},
                    )
                    continue

                device = DeviceService.get_active_by_name(db, pc_name)
                config = ConfigService.get_or_create(db)
                if not device:
                    await websocket_manager.send_json(
                        websocket,
                        {
                            "event_type": "device_not_found",
                            "message": "El equipo no existe o está inactivo",
                            "pc_name": pc_name,
                        },
                    )
                    continue

                await websocket_manager.send_json(
                    websocket,
                    {
                        "event_type": "device_configured",
                        "pc_name": device.nombre_pc,
                        "accion": device.accion,
                        "expected_image": "face_crop_base64",
                        "model_input": "128x128x3",
                        "manual_normalization": False,
                        "umbral_confianza_intruso": config.umbral_confianza_intruso,
                        "tiempo_minimo_entre_registros_segundos": config.tiempo_minimo_entre_registros_segundos,
                    },
                )
                continue

            if message_type == "frame":
                pc_name = payload.get("pc_name") or pc_name
                image_base64 = payload.get("image") or payload.get("image_base64")

                if not pc_name or not image_base64:
                    await websocket_manager.send_json(
                        websocket,
                        {"event_type": "invalid_frame", "message": "Debes enviar pc_name e image"},
                    )
                    continue

                try:
                    response = detection_service.process_base64_frame(db, pc_name, image_base64)
                    await websocket_manager.send_json(websocket, response.model_dump())
                except Exception as exc:
                    await websocket_manager.send_json(
                        websocket,
                        {"event_type": "processing_error", "message": str(exc)},
                    )
                continue

            await websocket_manager.send_json(
                websocket,
                {"event_type": "unknown_message", "message": "Tipo de mensaje no soportado"},
            )

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    finally:
        db.close()
