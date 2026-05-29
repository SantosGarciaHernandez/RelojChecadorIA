from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user_schema import UserResponse


class TrainingRegisterRequest(BaseModel):
    job_id: str = Field(..., min_length=8, max_length=80)
    numero_empleado: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=150)
    nombre_etiqueta_modelo: str = Field(..., max_length=100)
    correo: Optional[EmailStr] = None
    rol: str = Field(default="Usuario", max_length=30)
    activo: bool = True
    password: Optional[str] = Field(default=None, min_length=4)
    images_base64: list[str] = Field(..., min_length=1)

    @field_validator("job_id", "numero_empleado", "nombre", "nombre_etiqueta_modelo", "rol")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El campo no puede estar vacío")
        return value


class TrainingRegisterResponse(BaseModel):
    success: bool
    message: str
    job_id: str
    user: UserResponse | None = None
    model_labels: dict[str, str] | None = None
    train_images: int = 0
    validation_images: int = 0
