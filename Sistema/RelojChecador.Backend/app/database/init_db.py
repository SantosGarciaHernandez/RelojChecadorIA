from app.database.base import Base
from app.database.session import engine

# Importa modelos para que SQLAlchemy los registre en metadata.
from app.models import attendance_record_model, device_model, intruder_alert_model, system_config_model, user_model  # noqa: F401


def create_database_tables() -> None:
    Base.metadata.create_all(bind=engine)
