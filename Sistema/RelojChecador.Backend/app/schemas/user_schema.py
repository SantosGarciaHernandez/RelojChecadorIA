from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    numero_empleado: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=150)
    nombre_etiqueta_modelo: Optional[str] = Field(default=None, max_length=100)
    correo: Optional[EmailStr] = None
    rol: str = Field(default="Usuario", max_length=30)
    activo: bool = True


class UserCreate(UserBase):
    password: Optional[str] = Field(default=None, min_length=4)


class UserUpdate(BaseModel):
    numero_empleado: Optional[str] = Field(default=None, max_length=50)
    nombre: Optional[str] = Field(default=None, max_length=150)
    nombre_etiqueta_modelo: Optional[str] = Field(default=None, max_length=100)
    correo: Optional[EmailStr] = None
    rol: Optional[str] = Field(default=None, max_length=30)
    activo: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=4)


class UserResponse(UserBase):
    id_usuario: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)
