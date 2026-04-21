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
    from api.routes.practicas import router as practicas_router
    from api.routes.exenciones import router as exemptions_router
    from api.routes.tareas import router as tasks_router
    from api.routes.notificaciones import router as notifications_router
    from api.routes.opportunities import router as opportunities_router
    from api.routes.applications import router as applications_router
    from api.routes.role import router as role_router
    from api.routes.documents import router as documents_router    
    from api.routes.selection_process import router as selection_process_router    
    from api.routes.calificacion import router as calificacion_router
    from api.routes.interviews import router as interviews_router
    from api.routes.finalList import router as Final_list_router
    from api.routes.chat import router as chat_router
    from api.routes.opportunity_daily_notes import router as opportunity_daily_notes_router
    print("[STARTUP] Imports OK")
except Exception as e:
    print(f"[STARTUP] Import error: {e}")
    traceback.print_exc()
    raise

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "library")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("[STARTUP] Connecting to database...")
        create_db_and_tables()
        print("[STARTUP] Database OK")
    except Exception as e:
        print(f"[STARTUP] Database error: {e}")
        traceback.print_exc()
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    yield

app = FastAPI(lifespan=lifespan)

cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,https://localhost:3000,https://localhost,http://localhost"
).split(",")
cors_origins = [o.strip() for o in cors_origins if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(practicas_router)
app.include_router(exemptions_router)
app.include_router(tasks_router)
app.include_router(notifications_router)
app.include_router(opportunities_router)
app.include_router(applications_router)
app.include_router(role_router)
app.include_router(documents_router)
app.include_router(calificacion_router)
app.include_router(selection_process_router)
app.include_router(interviews_router)
app.include_router(Final_list_router)
app.include_router(chat_router)
app.include_router(opportunity_daily_notes_router)
