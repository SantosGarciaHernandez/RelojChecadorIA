from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Equipo(Base):
    __tablename__ = "Equipos"

    id_equipo: Mapped[int] = mapped_column("IdEquipo", Integer, primary_key=True, autoincrement=True)
    nombre_pc: Mapped[str] = mapped_column("NombrePc", String(100), unique=True, nullable=False, index=True)
    accion: Mapped[str] = mapped_column("Accion", String(20), nullable=False)  # Entrada | Salida
    activo: Mapped[bool] = mapped_column("Activo", Boolean, nullable=False, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column("FechaCreacion", DateTime, nullable=False, default=datetime.now)

    registros = relationship("RegistroUsuario", back_populates="equipo")
    intrusos = relationship("RegistroIntruso", back_populates="equipo")
