import os
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


load_dotenv()


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "clave-local-cambiar-en-produccion"
)

PASSWORD_RESET_SALT = os.getenv(
    "PASSWORD_RESET_SALT",
    "recuperacion-contrasena"
)

PASSWORD_RESET_EMPRESA_SALT = os.getenv(
    "PASSWORD_RESET_EMPRESA_SALT",
    "recuperacion-contrasena-empresa"
)

serializer = URLSafeTimedSerializer(SECRET_KEY)


# =====================================================
# TOKENS PARA USUARIOS
# =====================================================

def generar_token_recuperacion(email: str) -> str:
    return serializer.dumps(
        {
            "tipo": "usuario",
            "email": email
        },
        salt=PASSWORD_RESET_SALT
    )


def validar_token_recuperacion(token: str, expiracion_segundos: int = 900) -> str:
    try:
        data = serializer.loads(
            token,
            salt=PASSWORD_RESET_SALT,
            max_age=expiracion_segundos
        )

        if data.get("tipo") != "usuario":
            raise ValueError("El token no corresponde a un usuario.")

        return data["email"]

    except SignatureExpired:
        raise ValueError("El enlace de recuperación expiró.")

    except BadSignature:
        raise ValueError("El enlace de recuperación no es válido.")


# =====================================================
# TOKENS PARA EMPRESAS
# =====================================================

def generar_token_recuperacion_empresa(id_empresa: int, email: str) -> str:
    return serializer.dumps(
        {
            "tipo": "empresa",
            "id_empresa": id_empresa,
            "email": email
        },
        salt=PASSWORD_RESET_EMPRESA_SALT
    )


def validar_token_recuperacion_empresa(
    token: str,
    expiracion_segundos: int = 900
) -> dict:
    try:
        data = serializer.loads(
            token,
            salt=PASSWORD_RESET_EMPRESA_SALT,
            max_age=expiracion_segundos
        )

        if data.get("tipo") != "empresa":
            raise ValueError("El token no corresponde a una empresa.")

        return data

    except SignatureExpired:
        raise ValueError("El enlace de recuperación de empresa expiró.")

    except BadSignature:
        raise ValueError("El enlace de recuperación de empresa no es válido.")