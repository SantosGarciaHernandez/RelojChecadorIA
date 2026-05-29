import logging
import smtplib
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.intruder_alert_model import RegistroIntruso
from app.models.user_model import Usuario

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def get_guard_emails(db: Session) -> list[str]:
        stmt = select(Usuario).where(Usuario.activo == True, Usuario.rol.in_(["Guardia", "Administrador"]))
        users = db.execute(stmt).scalars().all()
        return [user.correo for user in users if user.correo]

    @staticmethod
    def send_intruder_alert(db: Session, alert: RegistroIntruso) -> None:
        settings = get_settings()
        if not settings.smtp_enabled:
            logger.info("SMTP desactivado. Alerta de intruso no enviada por correo.")
            return

        recipients = NotificationService.get_guard_emails(db)
        if not recipients:
            logger.warning("No hay correos de guardias/administradores para enviar alerta.")
            return

        subject = "ALERTA PRIORITARIA - Intruso detectado"
        body = (
            "Se detectó una persona no reconocida por el sistema RelojChecador IA.\n\n"
            f"ID alerta: {alert.id_intruso}\n"
            f"Fecha/hora: {alert.fecha_hora}\n"
            f"Ubicación lógica: {alert.tipo_ubicacion}\n"
            f"Confianza del modelo: {alert.confianza_modelo:.2%}\n"
            f"Estado: {alert.estado_alerta}\n"
        )

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.smtp_from or settings.smtp_username
        message["To"] = ", ".join(recipients)
        message.set_content(body)

        if alert.imagen_binaria:
            message.add_attachment(
                alert.imagen_binaria,
                maintype="image",
                subtype="jpeg",
                filename=f"intruso_{alert.id_intruso}.jpg",
            )

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
