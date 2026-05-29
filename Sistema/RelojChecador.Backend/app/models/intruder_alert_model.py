from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RegistroIntruso(Base):
    __tablename__ = "RegistroIntrusos"

    id_intruso: Mapped[int] = mapped_column("IdIntruso", Integer, primary_key=True, autoincrement=True)
    id_equipo: Mapped[int] = mapped_column("IdEquipo", Integer, ForeignKey("Equipos.IdEquipo"), nullable=False, index=True)
    tipo_ubicacion: Mapped[str] = mapped_column("TipoUbicacion", String(20), nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column("FechaHora", DateTime, nullable=False, default=datetime.now, index=True)
    confianza_modelo: Mapped[float] = mapped_column("ConfianzaModelo", Float, nullable=False)
    mensaje_alerta: Mapped[str] = mapped_column("MensajeAlerta", String(300), nullable=False)
    estado_alerta: Mapped[str] = mapped_column("EstadoAlerta", String(30), nullable=False, default="Pendiente")
    imagen_binaria: Mapped[bytes | None] = mapped_column("ImagenBinaria", LargeBinary, nullable=True)

    equipo = relationship("Equipo", back_populates="intrusos")
