import os
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import models

load_dotenv()

# Load database connection variables
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
port = os.getenv("DB_PORT", "5432")

# Build connection URL with Neon SSL parameters
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}?sslmode=require"

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    connect_args={"connect_timeout": 10},
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    _migrate_selection_process()

def _migrate_selection_process():
    """Add scheduled_start / scheduled_end columns if they don't exist yet."""
    try:
        with engine.connect() as conn:
            for col, col_type in [("scheduled_start", "TIMESTAMP"), ("scheduled_end", "TIMESTAMP")]:
                conn.execute(text(f"ALTER TABLE selection_process ADD COLUMN IF NOT EXISTS {col} {col_type}"))
            conn.commit()
    except Exception as e:
        print(f"[MIGRATE] selection_process migration skipped: {e}")

def get_session():
    with Session(engine) as session:
        yield session
