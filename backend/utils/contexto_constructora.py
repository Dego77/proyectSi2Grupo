from sqlmodel import Session, select
from sqlalchemy import func

from models import (
    Empresa,
    Usuario,
)


def obtener_contexto_constructora(session: Session) -> str:
    total_empresas = session.exec(
        select(func.count(Empresa.id_empresa))
    ).one()

    total_usuarios = session.exec(
        select(func.count(Usuario.id_usuarios))
    ).one()

    empresas = session.exec(
        select(Empresa).limit(5)
    ).all()

    usuarios = session.exec(
        select(Usuario).limit(5)
    ).all()

    empresas_texto = []
    for empresa in empresas:
        empresas_texto.append(
            f"- Empresa: {empresa.nombre}, email: {empresa.email}, estado: {empresa.estado}"
        )

    usuarios_texto = []
    for usuario in usuarios:
        nombre = getattr(usuario, "nombres", "") or ""
        apellido = getattr(usuario, "apellido", "") or ""
        email = getattr(usuario, "email", "") or ""

        usuarios_texto.append(
            f"- Usuario: {nombre} {apellido}, email: {email}"
        )

    contexto = f"""
Resumen de base de datos:
- Total de empresas: {total_empresas}
- Total de usuarios: {total_usuarios}

Empresas registradas:
{chr(10).join(empresas_texto)}

Usuarios registrados:
{chr(10).join(usuarios_texto)}
"""

    return contexto