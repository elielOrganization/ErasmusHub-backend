from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.database import create_db_and_tables
from api.routes.users import router as users_router
from api.routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# El Middleware SIEMPRE debe estar en el main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Solo incluimos el router. Él ya sabe qué hacer.
app.include_router(users_router)
app.include_router(auth_router)