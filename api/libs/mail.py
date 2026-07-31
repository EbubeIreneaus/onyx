from pathlib import Path

from fastapi_mail import ConnectionConfig
from setting import settings

conf = ConnectionConfig(
    MAIL_SERVER=settings.MAIL_HOST,
    MAIL_USERNAME=settings.MAIL_USER,
    MAIL_PASSWORD=settings.MAIL_PASS,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    TEMPLATE_FOLDER=Path(__file__).resolve().parent.parent / 'email_templates'
)