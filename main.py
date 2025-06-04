from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, create_engine, select
from models import *

database_url = "postgresql://localhost/course_management_db"

engine = create_engine(database_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()