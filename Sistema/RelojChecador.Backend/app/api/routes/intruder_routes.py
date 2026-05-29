from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.intruder_schema import IntruderResponse, MarkIntruderAttendedRequest
from app.services.intruder_alert_service import IntruderAlertService

router = APIRouter(prefix="/intruders", tags=["Intrusos"])


def _to_response(alert) -> IntruderResponse:
    return IntruderResponse(
        id_intruso=alert.id_intruso,
        id_equipo=alert.id_equipo,
        tipo_ubicacion=alert.tipo_ubicacion,
        fecha_hora=alert.fecha_hora,
        confianza_modelo=alert.confianza_modelo,
        mensaje_alerta=alert.mensaje_alerta,
        estado_alerta=alert.estado_alerta,
        nombre_pc=alert.equipo.nombre_pc if alert.equipo else None,
        tiene_imagen=bool(alert.imagen_binaria),
    )


@router.get("", response_model=list[IntruderResponse])
def list_intruders(
    limit: int = Query(default=100, ge=1, le=1000),
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    return [_to_response(alert) for alert in IntruderAlertService.list_alerts(db, limit=limit, status=status_filter)]


@router.get("/{intruder_id}", response_model=IntruderResponse)
def get_intruder(intruder_id: int, db: Session = Depends(get_db)):
    alert = IntruderAlertService.get(db, intruder_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta no encontrada")
    return _to_response(alert)


@router.get("/{intruder_id}/image")
def get_intruder_image(intruder_id: int, db: Session = Depends(get_db)):
    alert = IntruderAlertService.get(db, intruder_id)
    if not alert or not alert.imagen_binaria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagen no encontrada")
    return Response(content=alert.imagen_binaria, media_type="image/jpeg")


@router.put("/{intruder_id}/mark-as-attended", response_model=IntruderResponse)
def mark_as_attended(intruder_id: int, payload: MarkIntruderAttendedRequest, db: Session = Depends(get_db)):
    alert = IntruderAlertService.get(db, intruder_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta no encontrada")
    updated = IntruderAlertService.mark_as_attended(db, alert, status=payload.estado_alerta)
    return _to_response(updated)
