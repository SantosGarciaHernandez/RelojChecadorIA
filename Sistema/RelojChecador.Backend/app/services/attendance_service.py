from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attendance_record_model import RegistroUsuario
from app.models.device_model import Equipo
from app.models.system_config_model import ConfiguracionSistema
from app.models.user_model import Usuario


@dataclass
class AttendanceResult:
    registered: bool
    event_type: str
    message: str
    reason: str | None = None
    record: RegistroUsuario | None = None


class AttendanceService:
    @staticmethod
    def _recent_duplicate_exists(
        db: Session,
        user_id: int,
        device_id: int,
        seconds: int,
        now: datetime,
    ) -> bool:
        min_time = now - timedelta(seconds=seconds)
        stmt = (
            select(RegistroUsuario)
            .where(
                RegistroUsuario.id_usuario == user_id,
                RegistroUsuario.id_equipo == device_id,
                RegistroUsuario.fecha_hora >= min_time,
            )
            .order_by(RegistroUsuario.fecha_hora.desc())
        )
        return db.execute(stmt).scalars().first() is not None

    @staticmethod
    def _get_last_user_record(db: Session, user_id: int) -> RegistroUsuario | None:
        stmt = (
            select(RegistroUsuario)
            .where(RegistroUsuario.id_usuario == user_id)
            .order_by(RegistroUsuario.fecha_hora.desc())
        )
        return db.execute(stmt).scalars().first()

    @staticmethod
    def register_attendance(
        db: Session,
        user: Usuario,
        device: Equipo,
        confidence: float,
        config: ConfiguracionSistema,
    ) -> AttendanceResult:
        now = datetime.now()
        record_type = device.accion

        if AttendanceService._recent_duplicate_exists(
            db=db,
            user_id=user.id_usuario,
            device_id=device.id_equipo,
            seconds=config.tiempo_minimo_entre_registros_segundos,
            now=now,
        ):
            return AttendanceResult(
                registered=False,
                event_type="attendance_ignored",
                message="El usuario ya fue registrado recientemente",
                reason="Registro duplicado dentro del intervalo mínimo",
            )

        last_record = AttendanceService._get_last_user_record(db, user.id_usuario)

        if record_type == "Entrada" and not config.permitir_multiples_entradas:
            if last_record and last_record.tipo_registro == "Entrada":
                return AttendanceResult(
                    registered=False,
                    event_type="attendance_ignored",
                    message="Entrada ignorada por regla de múltiples entradas",
                    reason="El usuario ya tiene una entrada vigente sin salida posterior",
                )

        if record_type == "Salida" and not config.permitir_multiples_salidas:
            if not last_record or last_record.tipo_registro == "Salida":
                return AttendanceResult(
                    registered=False,
                    event_type="attendance_ignored",
                    message="Salida ignorada por regla de entrada/salida",
                    reason="No existe entrada vigente para este usuario",
                )

        record = RegistroUsuario(
            id_usuario=user.id_usuario,
            id_equipo=device.id_equipo,
            tipo_registro=record_type,
            fecha_hora=now,
            confianza_modelo=confidence,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return AttendanceResult(
            registered=True,
            event_type="attendance_registered",
            message=f"{record_type} registrada correctamente",
            record=record,
        )

    @staticmethod
    def list_records(db: Session, limit: int = 100) -> list[RegistroUsuario]:
        stmt = select(RegistroUsuario).order_by(RegistroUsuario.fecha_hora.desc()).limit(limit)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def recent(db: Session, limit: int = 20) -> list[RegistroUsuario]:
        return AttendanceService.list_records(db, limit=limit)
