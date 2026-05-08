import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()


def enviar_correo(destinatario: str, asunto: str, contenido: str):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user)

    if not smtp_user or not smtp_password:
        raise RuntimeError(
            "Faltan SMTP_USER o SMTP_PASSWORD en el archivo .env"
        )

    mensaje = EmailMessage()
    mensaje["From"] = smtp_from
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.set_content(contenido)

    with smtplib.SMTP(smtp_host, smtp_port) as servidor:
        servidor.starttls()
        servidor.login(smtp_user, smtp_password)
        servidor.send_message(mensaje)