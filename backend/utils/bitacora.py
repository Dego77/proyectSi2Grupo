from datetime import datetime
from typing import Optional

from sqlmodel import Session

from models import Bitacora


def registrar_bitacora(
    session: Session,
    id_usuario: int,
    modulo: str,
    accion: str,
    descripcion: Optional[str] = None,
):
    """
    Registra una acción importante dentro de la base de datos de la empresa.

    No lanza error hacia el usuario si falla la bitácora,
    para no bloquear la operación principal.
    """

    try:
        registro = Bitacora(
            id_usuarios=id_usuario,
            fecha_hora=datetime.utcnow(),
            modulo=modulo,
            accion=accion,
            descripcion=descripcion,
        )

        session.add(registro)
        session.commit()

    except Exception:
        session.rollback()