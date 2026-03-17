import os
from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
import models

load_dotenv()

# Extraer variables
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
port = os.getenv("DB_PORT", "5432")

# Reconstruir la URL con los parámetros de Neon
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}?sslmode=require"

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
