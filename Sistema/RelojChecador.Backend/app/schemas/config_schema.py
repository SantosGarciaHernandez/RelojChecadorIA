from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ConfigResponse(BaseModel):
    id_configuracion: int
    permitir_multiples_entradas: bool
    permitir_multiples_salidas: bool
    tiempo_minimo_entre_registros_segundos: int
    umbral_confianza_intruso: float
    alertas_sonoras_activas: bool
    correos_activos: bool

    model_config = ConfigDict(from_attributes=True)


class ConfigUpdate(BaseModel):
    permitir_multiples_entradas: Optional[bool] = None
    permitir_multiples_salidas: Optional[bool] = None
    tiempo_minimo_entre_registros_segundos: Optional[int] = Field(default=None, ge=1, le=3600)
    umbral_confianza_intruso: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    alertas_sonoras_activas: Optional[bool] = None
    correos_activos: Optional[bool] = None
