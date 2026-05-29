from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user_model import Usuario
from app.schemas.user_schema import UserCreate, UserUpdate


class UserService:
    @staticmethod
    def list(db: Session, only_active: bool | None = None) -> list[Usuario]:
        stmt = select(Usuario).order_by(Usuario.nombre)
        if only_active is not None:
            stmt = stmt.where(Usuario.activo == only_active)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get(db: Session, user_id: int) -> Usuario | None:
        return db.get(Usuario, user_id)

    @staticmethod
    def get_by_employee_or_email(db: Session, value: str) -> Usuario | None:
        stmt = select(Usuario).where(or_(Usuario.numero_empleado == value, Usuario.correo == value))
        return db.execute(stmt).scalars().first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.nombre == name)
        return db.execute(stmt).scalars().first()

    @staticmethod
    def get_by_model_label(db: Session, model_label: str) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.nombre_etiqueta_modelo == model_label)
        return db.execute(stmt).scalars().first()

    @staticmethod
    def create(db: Session, payload: UserCreate) -> Usuario:
        user = Usuario(
            numero_empleado=payload.numero_empleado,
            nombre=payload.nombre,
            nombre_etiqueta_modelo=payload.nombre_etiqueta_modelo,
            correo=str(payload.correo) if payload.correo else None,
            rol=payload.rol,
            activo=payload.activo,
            password_hash=get_password_hash(payload.password) if payload.password else None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user: Usuario, payload: UserUpdate) -> Usuario:
        data = payload.model_dump(exclude_unset=True)
        password = data.pop("password", None)
        for field, value in data.items():
            if field == "correo" and value is not None:
                value = str(value)
            setattr(user, field, value)
        if password:
            user.password_hash = get_password_hash(password)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def deactivate(db: Session, user: Usuario) -> Usuario:
        user.activo = False
        db.commit()
        db.refresh(user)
        return user
