import os
import re
from functools import lru_cache
from urllib.parse import quote_plus

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

import models
from database import get_session
from models import BaseDeDatosEmpresa


load_dotenv()


def limpiar_nombre_bd(texto: str) -> str:
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    texto = texto.strip("_")
    return texto[:40]


def construir_nombre_bd_empresa(id_empresa: int, nombre_empresa: str) -> str:
    nombre_limpio = limpiar_nombre_bd(nombre_empresa)
    return f"bd_empresa_{id_empresa}_{nombre_limpio}"


def construir_database_url(
    host: str,
    puerto: int,
    nombre_bd: str,
    usuario: str,
    password: str,
) -> str:
    usuario_seguro = quote_plus(usuario)
    password_seguro = quote_plus(password)

    return (
        f"postgresql://{usuario_seguro}:{password_seguro}"
        f"@{host}:{puerto}/{nombre_bd}"
    )


def crear_base_datos_postgres(nombre_bd: str):
    host = os.getenv("DB_ADMIN_HOST")
    port = os.getenv("DB_ADMIN_PORT", "5432")
    user = os.getenv("DB_ADMIN_USER")
    password = os.getenv("DB_ADMIN_PASSWORD")
    database = os.getenv("DB_ADMIN_DATABASE", "postgres")

    if not host or not user or not password:
        raise RuntimeError(
            "Faltan DB_ADMIN_HOST, DB_ADMIN_USER o DB_ADMIN_PASSWORD en el archivo .env"
        )

    conexion = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=database,
    )

    conexion.autocommit = True

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (nombre_bd,)
            )

            existe = cursor.fetchone()

            if not existe:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(nombre_bd)
                    )
                )
    finally:
        conexion.close()


def crear_tablas_empresa(database_url: str):
    engine_empresa = create_engine(database_url, echo=True)
    SQLModel.metadata.create_all(engine_empresa)
    return engine_empresa


@lru_cache(maxsize=100)
def obtener_engine_empresa(database_url: str):
    return create_engine(database_url, echo=True)


def construir_database_url_empresa(config: BaseDeDatosEmpresa) -> str:
    return construir_database_url(
        host=config.host,
        puerto=config.puerto,
        nombre_bd=config.nombre_bd,
        usuario=config.usuario_bd,
        password=config.password_bd,
    )


def get_session_empresa(
    x_empresa_id: int = Header(..., alias="X-Empresa-Id"),
    session_central: Session = Depends(get_session),
):
    config_bd = session_central.exec(
        select(BaseDeDatosEmpresa).where(
            BaseDeDatosEmpresa.id_empresa == x_empresa_id,
            BaseDeDatosEmpresa.estado == True,
        )
    ).first()

    if not config_bd:
        raise HTTPException(
            status_code=404,
            detail="No se encontró una base de datos activa para esta empresa.",
        )

    database_url = construir_database_url_empresa(config_bd)
    engine_empresa = obtener_engine_empresa(database_url)

    with Session(engine_empresa) as session_empresa:
        yield session_empresa