from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DeviceBase(BaseModel):
    nombre_pc: str = Field(..., max_length=100)
    accion: str = Field(..., pattern="^(Entrada|Salida)$")
    activo: bool = True


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    nombre_pc: Optional[str] = Field(default=None, max_length=100)
    accion: Optional[str] = Field(default=None, pattern="^(Entrada|Salida)$")
    activo: Optional[bool] = None


class DeviceResponse(DeviceBase):
    id_equipo: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)
