import json
from functools import lru_cache
from pathlib import Path
from typing import List
from urllib.parse import quote_plus

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RelojChecador IA API"
    environment: str = "development"
    debug: bool = True
    api_prefix: str = "/api"
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"])

    sql_server: str = "localhost"
    sql_database: str = "RelojChecadorIA"
    sql_username: str = "sa"
    sql_password: str = ""
    sql_driver: str = "ODBC Driver 18 for SQL Server"
    sql_trust_server_certificate: str = "yes"
    sql_encrypt: str = "no"

    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    # Modelo real del proyecto. Fue guardado en formato Keras moderno (.keras).
    model_path: str = "app/ml/trained_model.keras"
    labels_path: str = "app/ml/labels.json"
    model_input_width: int = 128
    model_input_height: int = 128
    model_input_channels: int = 3

    # El modelo ya incluye una capa Rescaling(1./255), por eso la API NO divide entre 255.
    model_normalize_input: bool = False

    # La imagen que manda el frontend debe ser una cara ya recortada.
    frontend_sends_face_crop: bool = True

    # Si la confianza es menor al umbral, se registra como intruso aunque la clase superior no sea "Intruso".
    default_intruder_threshold: float = 0.70
    intruder_label_name: str = "Intruso"

    # Cantidad mínima de predicciones consecutivas del mismo usuario/equipo
    # antes de guardar entrada/salida. Sirve para evitar falsos positivos.
    attendance_required_consecutive_validations: int = 3


    # Entrenamiento desde el frontend.
    training_dataset_dir: str = "app/ml/training_dataset"
    training_output_dir: str = "app/ml/training_output"
    training_capture_total_images: int = 320
    training_train_image_count: int = 220
    training_validation_image_count: int = 100
    training_epochs: int = 40
    training_batch_size: int = 16
    training_seed: int = 47
    training_early_stopping_patience: int = 8

    auto_create_tables: bool = False

    smtp_enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return []
            if text.startswith("["):
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, list):
                        return [str(origin).strip() for origin in parsed if str(origin).strip()]
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in text.split(",") if origin.strip()]
        return value

    @property
    def database_url(self) -> str:
        connection = (
            f"DRIVER={{{self.sql_driver}}};"
            f"SERVER={self.sql_server};"
            f"DATABASE={self.sql_database};"
            f"UID={self.sql_username};"
            f"PWD={self.sql_password};"
            f"TrustServerCertificate={self.sql_trust_server_certificate};"
            f"Encrypt={self.sql_encrypt};"
        )
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(connection)}"

    @property
    def absolute_model_path(self) -> Path:
        return Path(self.model_path).resolve()

    @property
    def absolute_labels_path(self) -> Path:
        return Path(self.labels_path).resolve()

    @property
    def absolute_training_dataset_dir(self) -> Path:
        return Path(self.training_dataset_dir).resolve()

    @property
    def absolute_training_train_dir(self) -> Path:
        return self.absolute_training_dataset_dir / "Train"

    @property
    def absolute_training_validation_dir(self) -> Path:
        return self.absolute_training_dataset_dir / "Validation"

    @property
    def absolute_training_output_dir(self) -> Path:
        return Path(self.training_output_dir).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
