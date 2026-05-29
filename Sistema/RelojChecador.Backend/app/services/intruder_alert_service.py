from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.device_model import Equipo
from app.models.intruder_alert_model import RegistroIntruso


class IntruderAlertService:
    @staticmethod
    def create_alert(
        db: Session,
        device: Equipo,
        confidence: float,
        image_bytes: bytes | None,
        message: str = "Intruso detectado",
    ) -> RegistroIntruso:
        alert = RegistroIntruso(
            id_equipo=device.id_equipo,
            tipo_ubicacion=device.accion,
            fecha_hora=datetime.now(),
            confianza_modelo=confidence,
            mensaje_alerta=message,
            estado_alerta="Pendiente",
            imagen_binaria=image_bytes,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def list_alerts(db: Session, limit: int = 100, status: str | None = None) -> list[RegistroIntruso]:
        stmt = select(RegistroIntruso).order_by(RegistroIntruso.fecha_hora.desc()).limit(limit)
        if status:
            stmt = stmt.where(RegistroIntruso.estado_alerta == status)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get(db: Session, intruder_id: int) -> RegistroIntruso | None:
        return db.get(RegistroIntruso, intruder_id)

    @staticmethod
    def mark_as_attended(db: Session, alert: RegistroIntruso, status: str = "Atendida") -> RegistroIntruso:
        alert.estado_alerta = status
        db.commit()
        db.refresh(alert)
        return alert
