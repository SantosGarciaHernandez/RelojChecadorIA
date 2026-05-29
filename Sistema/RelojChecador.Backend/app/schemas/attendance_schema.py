from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttendanceResponse(BaseModel):
    id_registro: int
    id_usuario: int
    id_equipo: int
    tipo_registro: str
    fecha_hora: datetime
    confianza_modelo: float
    nombre_usuario: str | None = None
    numero_empleado: str | None = None
    nombre_pc: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RecentAttendanceResponse(BaseModel):
    records: list[AttendanceResponse]
