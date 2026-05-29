from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IntruderResponse(BaseModel):
    id_intruso: int
    id_equipo: int
    tipo_ubicacion: str
    fecha_hora: datetime
    confianza_modelo: float
    mensaje_alerta: str
    estado_alerta: str
    nombre_pc: str | None = None
    tiene_imagen: bool = False

    model_config = ConfigDict(from_attributes=True)


class MarkIntruderAttendedRequest(BaseModel):
    estado_alerta: str = "Atendida"
