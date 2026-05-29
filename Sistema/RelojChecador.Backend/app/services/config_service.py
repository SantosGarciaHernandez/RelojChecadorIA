from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.system_config_model import ConfiguracionSistema
from app.schemas.config_schema import ConfigUpdate


class ConfigService:
    @staticmethod
    def get_or_create(db: Session) -> ConfiguracionSistema:
        config = db.execute(select(ConfiguracionSistema).order_by(ConfiguracionSistema.id_configuracion)).scalars().first()
        if config:
            return config

        settings = get_settings()
        config = ConfiguracionSistema(
            permitir_multiples_entradas=False,
            permitir_multiples_salidas=False,
            tiempo_minimo_entre_registros_segundos=60,
            umbral_confianza_intruso=settings.default_intruder_threshold,
            alertas_sonoras_activas=True,
            correos_activos=False,
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return config

    @staticmethod
    def update(db: Session, payload: ConfigUpdate) -> ConfiguracionSistema:
        config = ConfigService.get_or_create(db)
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        db.commit()
        db.refresh(config)
        return config
