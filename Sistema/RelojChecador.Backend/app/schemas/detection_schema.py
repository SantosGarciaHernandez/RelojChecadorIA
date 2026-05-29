from typing import Any, Optional

from pydantic import BaseModel, Field


class DetectionFrameRequest(BaseModel):
    pc_name: str = Field(..., description="Nombre del equipo que está detectando")
    image_base64: str = Field(..., description="Cara recortada en base64. Acepta data URL o base64 puro")


class DetectionResponse(BaseModel):
    event_type: str
    recognized: bool = False
    user_id: Optional[int] = None
    employee_number: Optional[str] = None
    name: Optional[str] = None
    record_type: Optional[str] = None
    confidence: Optional[float] = None
    timestamp: Optional[str] = None
    message: str
    reason: Optional[str] = None
    extra: dict[str, Any] = Field(default_factory=dict)
