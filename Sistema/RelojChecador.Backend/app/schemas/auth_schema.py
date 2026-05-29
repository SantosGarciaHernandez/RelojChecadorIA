from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    usuario: str = Field(..., description="Correo o número de empleado")
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id_usuario: int
    nombre: str
    rol: str
