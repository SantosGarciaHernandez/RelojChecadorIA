from collections import defaultdict
from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attendance_record_model import RegistroUsuario
from app.models.device_model import Equipo
from app.models.intruder_alert_model import RegistroIntruso
from app.models.user_model import Usuario
from app.schemas.dashboard_schema import DashboardSummary, IntrudersByDayItem, RecordsByHourItem


class DashboardService:
    @staticmethod
    def summary(db: Session) -> DashboardSummary:
        today_start = datetime.combine(date.today(), time.min)
        today_end = datetime.combine(date.today(), time.max)

        usuarios_activos = len(db.execute(select(Usuario).where(Usuario.activo == True)).scalars().all())
        equipos_activos = len(db.execute(select(Equipo).where(Equipo.activo == True)).scalars().all())
        registros_hoy = len(
            db.execute(
                select(RegistroUsuario).where(
                    RegistroUsuario.fecha_hora >= today_start,
                    RegistroUsuario.fecha_hora <= today_end,
                )
            ).scalars().all()
        )
        intrusos_pendientes = len(
            db.execute(select(RegistroIntruso).where(RegistroIntruso.estado_alerta == "Pendiente")).scalars().all()
        )
        intrusos_hoy = len(
            db.execute(
                select(RegistroIntruso).where(
                    RegistroIntruso.fecha_hora >= today_start,
                    RegistroIntruso.fecha_hora <= today_end,
                )
            ).scalars().all()
        )

        return DashboardSummary(
            usuarios_activos=usuarios_activos,
            equipos_activos=equipos_activos,
            registros_hoy=registros_hoy,
            intrusos_pendientes=intrusos_pendientes,
            intrusos_hoy=intrusos_hoy,
        )

    @staticmethod
    def records_by_hour(db: Session) -> list[RecordsByHourItem]:
        today_start = datetime.combine(date.today(), time.min)
        today_end = datetime.combine(date.today(), time.max)
        records = db.execute(
            select(RegistroUsuario).where(
                RegistroUsuario.fecha_hora >= today_start,
                RegistroUsuario.fecha_hora <= today_end,
            )
        ).scalars().all()

        buckets = {hour: {"Entrada": 0, "Salida": 0} for hour in range(24)}
        for record in records:
            buckets[record.fecha_hora.hour][record.tipo_registro] += 1

        return [
            RecordsByHourItem(hour=hour, entradas=values["Entrada"], salidas=values["Salida"])
            for hour, values in buckets.items()
        ]

    @staticmethod
    def intruders_by_day(db: Session, days: int = 7) -> list[IntrudersByDayItem]:
        alerts = db.execute(select(RegistroIntruso).order_by(RegistroIntruso.fecha_hora.desc()).limit(1000)).scalars().all()
        counts: dict[str, int] = defaultdict(int)
        for alert in alerts:
            counts[alert.fecha_hora.date().isoformat()] += 1
        return [IntrudersByDayItem(date=day, total=total) for day, total in sorted(counts.items(), reverse=True)[:days]]
