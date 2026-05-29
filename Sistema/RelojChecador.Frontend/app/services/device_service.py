from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.device_model import Equipo
from app.schemas.device_schema import DeviceCreate, DeviceUpdate


class DeviceService:
    @staticmethod
    def list(db: Session, only_active: bool | None = None) -> list[Equipo]:
        stmt = select(Equipo).order_by(Equipo.nombre_pc)
        if only_active is not None:
            stmt = stmt.where(Equipo.activo == only_active)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get(db: Session, device_id: int) -> Equipo | None:
        return db.get(Equipo, device_id)

    @staticmethod
    def get_by_name(db: Session, pc_name: str) -> Equipo | None:
        stmt = select(Equipo).where(Equipo.nombre_pc == pc_name)
        return db.execute(stmt).scalars().first()

    @staticmethod
    def get_active_by_name(db: Session, pc_name: str) -> Equipo | None:
        stmt = select(Equipo).where(Equipo.nombre_pc == pc_name, Equipo.activo == True)
        return db.execute(stmt).scalars().first()

    @staticmethod
    def create(db: Session, payload: DeviceCreate) -> Equipo:
        device = Equipo(nombre_pc=payload.nombre_pc, accion=payload.accion, activo=payload.activo)
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def update(db: Session, device: Equipo, payload: DeviceUpdate) -> Equipo:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(device, field, value)
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def deactivate(db: Session, device: Equipo) -> Equipo:
        device.activo = False
        db.commit()
        db.refresh(device)
        return device
