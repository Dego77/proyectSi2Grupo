import os
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import create_engine, Session


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH, override=True)


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("Falta DATABASE_URL en el archivo backend/.env")


engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session