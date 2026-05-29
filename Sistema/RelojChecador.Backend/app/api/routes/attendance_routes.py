from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.attendance_schema import AttendanceResponse
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Registros"])


def _to_response(record) -> AttendanceResponse:
    return AttendanceResponse(
        id_registro=record.id_registro,
        id_usuario=record.id_usuario,
        id_equipo=record.id_equipo,
        tipo_registro=record.tipo_registro,
        fecha_hora=record.fecha_hora,
        confianza_modelo=record.confianza_modelo,
        nombre_usuario=record.usuario.nombre if record.usuario else None,
        numero_empleado=record.usuario.numero_empleado if record.usuario else None,
        nombre_pc=record.equipo.nombre_pc if record.equipo else None,
    )


@router.get("", response_model=list[AttendanceResponse])
def list_attendance(limit: int = Query(default=100, ge=1, le=1000), db: Session = Depends(get_db)):
    return [_to_response(record) for record in AttendanceService.list_records(db, limit=limit)]


@router.get("/recent", response_model=list[AttendanceResponse])
def recent_attendance(limit: int = Query(default=10, ge=1, le=100), db: Session = Depends(get_db)):
    return [_to_response(record) for record in AttendanceService.recent(db, limit=limit)]
