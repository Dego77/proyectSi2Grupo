from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
from database import engine
import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    print(SQLModel.metadata.tables.keys())
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def inicio():
    return {"mensaje": "Backend funcionando"}