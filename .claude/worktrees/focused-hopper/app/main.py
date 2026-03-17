from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.database import create_db_and_tables
# 1. Importa el router que creamos en el archivo de rutas
from api.routes.users import router as users_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea las tablas si no existen al arrancar
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# 2. Incluye las rutas de usuarios
# El prefix "/api/v1" es opcional pero recomendado para versionar tu API
app.include_router(users_router, prefix="/api/v1")

