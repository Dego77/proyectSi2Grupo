from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "postgresql://postgres:1234@127.0.0.1:5432/proysi2grup"

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session