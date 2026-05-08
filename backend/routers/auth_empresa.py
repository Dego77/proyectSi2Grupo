import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

from database import get_session
from models import Empresa
from utils.email import enviar_correo
from utils.tokens import (
    generar_token_recuperacion_empresa,
    validar_token_recuperacion_empresa,
)


load_dotenv()
print("DEBUG_SKIP_EMAIL:", repr(os.getenv("DEBUG_SKIP_EMAIL")))


router = APIRouter(
    prefix="/auth/empresa",
    tags=["Auth - Recuperación de contraseña Empresa"]
)


class SolicitarRecuperacionEmpresaRequest(BaseModel):
    email: str = Field(..., min_length=5)


class SolicitarRecuperacionEmpresaResponse(BaseModel):
    mensaje: str
    reset_link: Optional[str] = None


class VerificarTokenEmpresaResponse(BaseModel):
    mensaje: str
    id_empresa: int
    email: str


class RestablecerContrasenaEmpresaRequest(BaseModel):
    token: str = Field(..., min_length=10)
    nueva_contrasena: str = Field(..., min_length=4)


class RestablecerContrasenaEmpresaResponse(BaseModel):
    mensaje: str


@router.post(
    "/solicitar-recuperacion",
    response_model=SolicitarRecuperacionEmpresaResponse
)
def solicitar_recuperacion_empresa(
    datos: SolicitarRecuperacionEmpresaRequest,
    session: Session = Depends(get_session),
):
    """
    La empresa escribe su correo.
    FastAPI verifica si existe en la tabla empresa.
    Si existe, genera un token y envía un link de recuperación.
    """

    email_normalizado = datos.email.strip().lower()

    empresa = session.exec(
        select(Empresa).where(func.lower(Empresa.email) == email_normalizado)
    ).first()

    mensaje_generico = "Si el correo está registrado, se enviará un enlace de recuperación."

    if not empresa:
        return {
            "mensaje": mensaje_generico,
            "reset_link": None
        }

    token = generar_token_recuperacion_empresa(
        id_empresa=empresa.id_empresa,
        email=email_normalizado
    )

    reset_password_url = os.getenv(
        "RESET_PASSWORD_EMPRESA_FRONTEND_URL",
        "http://localhost:4200/empresa/restablecer-contrasena"
    )

    link_recuperacion = f"{reset_password_url}?token={token}"

    asunto = "Recuperación de contraseña - Empresa"

    contenido = f"""
Hola {empresa.nombre},

Recibimos una solicitud para restablecer la contraseña de acceso de la empresa.

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
                destinatario=empresa.email,
                asunto=asunto,
                contenido=contenido,
            )
        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"No se pudo enviar el correo de recuperación de empresa: {str(error)}"
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
    response_model=VerificarTokenEmpresaResponse
)
def verificar_token_empresa(token: str):
    """
    Verifica si el token de recuperación de empresa es válido.
    """

    try:
        data = validar_token_recuperacion_empresa(token)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    return {
        "mensaje": "Token de empresa válido.",
        "id_empresa": data["id_empresa"],
        "email": data["email"]
    }


@router.post(
    "/restablecer-contrasena",
    response_model=RestablecerContrasenaEmpresaResponse
)
def restablecer_contrasena_empresa(
    datos: RestablecerContrasenaEmpresaRequest,
    session: Session = Depends(get_session),
):
    """
    La empresa envía token + nueva contraseña.
    FastAPI valida el token.
    Si es válido, actualiza empresa.contrasena en PostgreSQL.
    """

    try:
        data = validar_token_recuperacion_empresa(datos.token)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    id_empresa = data["id_empresa"]
    email = data["email"]

    empresa = session.exec(
        select(Empresa).where(
            Empresa.id_empresa == id_empresa,
            func.lower(Empresa.email) == email.lower()
        )
    ).first()

    if not empresa:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada."
        )

    empresa.contrasena = datos.nueva_contrasena

    try:
        session.add(empresa)
        session.commit()
        session.refresh(empresa)
    except SQLAlchemyError as error:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo actualizar la contraseña de la empresa: {str(error)}"
        )

    return {
        "mensaje": "Contraseña de empresa actualizada correctamente."
    }