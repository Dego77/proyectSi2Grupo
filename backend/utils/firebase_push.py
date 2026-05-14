import os
from typing import Optional, Dict

import firebase_admin
from firebase_admin import credentials, messaging
from dotenv import load_dotenv


load_dotenv()


def inicializar_firebase():
    """
    Inicializa Firebase Admin SDK una sola vez.
    Usa el archivo JSON de credenciales definido en FIREBASE_CREDENTIALS_PATH.
    """

    if firebase_admin._apps:
        return

    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

    if not credentials_path:
        raise RuntimeError(
            "Falta FIREBASE_CREDENTIALS_PATH en el archivo .env"
        )

    cred = credentials.Certificate(credentials_path)
    firebase_admin.initialize_app(cred)


def enviar_push_a_token(
    token: str,
    titulo: str,
    mensaje: str,
    data: Optional[Dict[str, str]] = None,
) -> str:
    """
    Envía una notificación push real a un dispositivo usando FCM token.
    """

    inicializar_firebase()

    data_limpia = {}

    if data:
        data_limpia = {
            str(clave): str(valor)
            for clave, valor in data.items()
            if valor is not None
        }

    message = messaging.Message(
        notification=messaging.Notification(
            title=titulo,
            body=mensaje,
        ),
        data=data_limpia,
        token=token,
    )

    respuesta = messaging.send(message)

    return respuesta