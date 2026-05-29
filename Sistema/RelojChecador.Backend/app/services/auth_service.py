from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, decode_access_token, verify_password
from app.database.session import get_db
from app.models.user_model import Usuario
from app.services.user_service import UserService

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


class AuthService:
    @staticmethod
    def authenticate(db: Session, usuario: str, password: str) -> Usuario | None:
        user = UserService.get_by_employee_or_email(db, usuario)
        if not user or not user.activo:
            return None
        if not verify_password(password, user.password_hash or ""):
            return None
        return user

    @staticmethod
    def build_token(user: Usuario) -> str:
        return create_access_token(
            subject=str(user.id_usuario),
            extra_claims={"rol": user.rol, "nombre": user.nombre, "numero_empleado": user.numero_empleado},
        )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido") from exc

    user = db.get(Usuario, user_id)
    if not user or not user.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autorizado")
    return user


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.rol != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere rol Administrador")
    return current_user
