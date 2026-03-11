import os
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

print("[STARTUP] Importing modules...")

try:
    from core.database import create_db_and_tables
    from api.routes.users import router as users_router
    from api.routes.auth import router as auth_router
    print("[STARTUP] Imports OK")
except Exception as e:
    print(f"[STARTUP] Import error: {e}")
    traceback.print_exc()
    raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("[STARTUP] Connecting to database...")
        create_db_and_tables()
        print("[STARTUP] Database OK")
    except Exception as e:
        print(f"[STARTUP] Database error: {e}")
        traceback.print_exc()
        # No re-raise: let the app start even if DB init fails
        # Tables already exist in Neon, this is just a safety check
    yield

app = FastAPI(lifespan=lifespan)

# CORS: lee origenes permitidos de la env var CORS_ORIGINS (separados por coma)
# Default: http://localhost:3000 para desarrollo local
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Solo incluimos el router. Él ya sabe qué hacer.
app.include_router(users_router)
app.include_router(auth_router)