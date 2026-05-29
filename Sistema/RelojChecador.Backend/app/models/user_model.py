from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Usuario(Base):
    __tablename__ = "Usuarios"

    id_usuario: Mapped[int] = mapped_column("IdUsuario", Integer, primary_key=True, autoincrement=True)
    numero_empleado: Mapped[str] = mapped_column("NumeroEmpleado", String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column("Nombre", String(150), nullable=False)

    # Debe coincidir con labels.json: SantosSet, NaomiSet, DanielSet, etc.
    # La clase "Intruso" NO se registra en Usuarios.
    nombre_etiqueta_modelo: Mapped[str | None] = mapped_column(
        "NombreEtiquetaModelo", String(100), nullable=True, index=True
    )

    correo: Mapped[str | None] = mapped_column("Correo", String(150), nullable=True)
    rol: Mapped[str] = mapped_column("Rol", String(30), nullable=False, default="Usuario")
    activo: Mapped[bool] = mapped_column("Activo", Boolean, nullable=False, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column("FechaCreacion", DateTime, nullable=False, default=datetime.now)

    # Campo necesario para login administrativo. Si ya tienes una tabla existente, agrega esta columna o ajusta AuthService.
    password_hash: Mapped[str | None] = mapped_column("PasswordHash", String(255), nullable=True)

    registros = relationship("RegistroUsuario", back_populates="usuario")
