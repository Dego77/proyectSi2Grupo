from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

from database import engine
import models

from routers import incluir_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    print("Tablas registradas:")
    print(SQLModel.metadata.tables.keys())
    yield


app = FastAPI(
    title="Backend FastAPI PostgreSQL Multiempresa",
    description="API modular para sistema multiempresa con FastAPI y PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Inicio"])
def inicio():
    return {"mensaje": "Backend funcionando"}


@app.get("/health", tags=["Inicio"])
def health():
    return {"status": "ok"}


incluir_routers(app)