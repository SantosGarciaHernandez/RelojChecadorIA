import asyncio
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database.session import SessionLocal
from app.services.attendance_service import AttendanceService

router = APIRouter(tags=["WebSockets"])


def _serialize_record(record) -> dict:
    return {
        "id_registro": record.id_registro,
        "id_usuario": record.id_usuario,
        "id_equipo": record.id_equipo,
        "tipo_registro": record.tipo_registro,
        "fecha_hora": record.fecha_hora.isoformat() if record.fecha_hora else None,
        "confianza_modelo": record.confianza_modelo,
        "nombre_usuario": record.usuario.nombre if record.usuario else None,
        "numero_empleado": record.usuario.numero_empleado if record.usuario else None,
        "nombre_pc": record.equipo.nombre_pc if record.equipo else None,
    }


def _records_signature(records) -> tuple:
    return tuple((record.id_registro, record.fecha_hora) for record in records)


@router.websocket("/ws/attendance/recent")
async def recent_attendance_websocket(websocket: WebSocket):
    """
    Envía los últimos registros por WebSocket.

    Para este proyecto se usa un polling ligero del lado servidor:
    - Al conectar envía la tabla inicial.
    - Cada segundo revisa si cambió el último registro.
    - Solo vuelve a enviar cuando hay cambios.

    Esto evita acoplar el registro de asistencia con lógica async y mantiene
    una actualización prácticamente en tiempo real para la UI.
    """
    await websocket.accept()
    db = SessionLocal()
    last_signature: tuple | None = None

    try:
        while True:
            records = AttendanceService.recent(db, limit=10)
            signature = _records_signature(records)

            if signature != last_signature:
                last_signature = signature
                await websocket.send_json(
                    {
                        "event_type": "attendance_recent_update",
                        "generated_at": datetime.now().isoformat(),
                        "records": [_serialize_record(record) for record in records],
                    }
                )

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
    finally:
        db.close()
