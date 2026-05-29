from sqlalchemy import Boolean, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ConfiguracionSistema(Base):
    __tablename__ = "ConfiguracionSistema"

    id_configuracion: Mapped[int] = mapped_column("IdConfiguracion", Integer, primary_key=True, autoincrement=True)
    permitir_multiples_entradas: Mapped[bool] = mapped_column("PermitirMultiplesEntradas", Boolean, nullable=False, default=False)
    permitir_multiples_salidas: Mapped[bool] = mapped_column("PermitirMultiplesSalidas", Boolean, nullable=False, default=False)
    tiempo_minimo_entre_registros_segundos: Mapped[int] = mapped_column("TiempoMinimoEntreRegistrosSegundos", Integer, nullable=False, default=60)
    umbral_confianza_intruso: Mapped[float] = mapped_column("UmbralConfianzaIntruso", Float, nullable=False, default=0.70)
    alertas_sonoras_activas: Mapped[bool] = mapped_column("AlertasSonorasActivas", Boolean, nullable=False, default=True)
    correos_activos: Mapped[bool] = mapped_column("CorreosActivos", Boolean, nullable=False, default=False)
