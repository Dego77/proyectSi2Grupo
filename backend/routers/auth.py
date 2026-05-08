import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

from database import get_session
from models import Usuario
from utils.email import enviar_correo
from utils.tokens import generar_token_recuperacion, validar_token_recuperacion


load_dotenv()


router = APIRouter(
    prefix="/auth",
    tags=["Auth - Recuperación de contraseña Usuario"]
)


class SolicitarRecuperacionRequest(BaseModel):
    email: str = Field(..., min_length=5)


class SolicitarRecuperacionResponse(BaseModel):
    mensaje: str
    reset_link: Optional[str] = None


class VerificarTokenResponse(BaseModel):
    mensaje: str
    email: str


class RestablecerContrasenaRequest(BaseModel):
    token: str = Field(..., min_length=10)
    nueva_contrasena: str = Field(..., min_length=4)


class RestablecerContrasenaResponse(BaseModel):
    mensaje: str


@router.post(
    "/solicitar-recuperacion",
    response_model=SolicitarRecuperacionResponse
)
def solicitar_recuperacion(
    datos: SolicitarRecuperacionRequest,
    session: Session = Depends(get_session),
):
    email_normalizado = datos.email.strip().lower()

    usuario = session.exec(
        select(Usuario).where(func.lower(Usuario.email) == email_normalizado)
    ).first()

    mensaje_generico = "Si el correo está registrado, se enviará un enlace de recuperación."

    if not usuario:
        return {
            "mensaje": mensaje_generico,
            "reset_link": None
        }

    token = generar_token_recuperacion(email_normalizado)

    reset_password_url = os.getenv(
        "RESET_PASSWORD_FRONTEND_URL",
        "http://localhost:4200/restablecer-contrasena"
    )

    link_recuperacion = f"{reset_password_url}?token={token}"

    nombre_usuario = getattr(usuario, "nombres", None) or getattr(
        usuario,
        "nombresusuario",
        "usuario"
    )

    asunto = "Recuperación de contraseña - Usuario"

    contenido = f"""
Hola {nombre_usuario},

Recibimos una solicitud para restablecer la contraseña de tu cuenta de usuario.

Para crear una nueva contraseña, ingresa al siguiente enlace:

{link_recuperacion}

Este enlace vencerá en 15 minutos.

Si no solicitaste este cambio, puedes ignorar este mensaje.

Atentamente,
Sistema Multiempresa
"""

    debug_skip_email = os.getenv(
        "DEBUG_SKIP_EMAIL",
        "false"
    ).lower() == "true"

    if not debug_skip_email:
        try:
            enviar_correo(
                destinatario=usuario.email,
                asunto=asunto,
                contenido=contenido,
            )
        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"No se pudo enviar el correo de recuperación de usuario: {str(error)}"
            )

    debug_return_reset_link = os.getenv(
        "DEBUG_RETURN_RESET_LINK",
        "false"
    ).lower() == "true"

    return {
        "mensaje": mensaje_generico,
        "reset_link": link_recuperacion if debug_return_reset_link else None
    }


@router.get(
    "/verificar-token",
    response_model=VerificarTokenResponse
)
def verificar_token(token: str):
    try:
        email = validar_token_recuperacion(token)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    return {
        "mensaje": "Token de usuario válido.",
        "email": email
    }


@router.post(
    "/restablecer-contrasena",
    response_model=RestablecerContrasenaResponse
)
def restablecer_contrasena(
    datos: RestablecerContrasenaRequest,
    session: Session = Depends(get_session),
):
    try:
        email = validar_token_recuperacion(datos.token)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    usuario = session.exec(
        select(Usuario).where(func.lower(Usuario.email) == email.lower())
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado."
        )

    usuario.contrasena = datos.nueva_contrasena

    try:
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
    except SQLAlchemyError as error:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo actualizar la contraseña del usuario: {str(error)}"
        )

    return {
        "mensaje": "Contraseña de usuario actualizada correctamente."
    }