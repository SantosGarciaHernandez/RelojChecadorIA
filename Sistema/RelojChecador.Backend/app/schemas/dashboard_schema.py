from pydantic import BaseModel


class DashboardSummary(BaseModel):
    usuarios_activos: int
    equipos_activos: int
    registros_hoy: int
    intrusos_pendientes: int
    intrusos_hoy: int


class RecordsByHourItem(BaseModel):
    hour: int
    entradas: int
    salidas: int


class IntrudersByDayItem(BaseModel):
    date: str
    total: int
