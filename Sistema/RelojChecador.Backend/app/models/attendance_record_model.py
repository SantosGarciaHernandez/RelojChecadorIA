from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RegistroUsuario(Base):
    __tablename__ = "RegistroUsuarios"

    id_registro: Mapped[int] = mapped_column("IdRegistro", Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column("IdUsuario", Integer, ForeignKey("Usuarios.IdUsuario"), nullable=False, index=True)
    id_equipo: Mapped[int] = mapped_column("IdEquipo", Integer, ForeignKey("Equipos.IdEquipo"), nullable=False, index=True)
    tipo_registro: Mapped[str] = mapped_column("TipoRegistro", String(20), nullable=False)  # Entrada | Salida
    fecha_hora: Mapped[datetime] = mapped_column("FechaHora", DateTime, nullable=False, default=datetime.now, index=True)
    confianza_modelo: Mapped[float] = mapped_column("ConfianzaModelo", Float, nullable=False)

    usuario = relationship("Usuario", back_populates="registros")
    equipo = relationship("Equipo", back_populates="registros")
