import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
import app.models  # noqa: F401 — registers ALL models with Base before create_all
from app.models.target import ExplorationTarget
from app.api.routes import study_areas
from app.api import targets, ml, field_notes, data_import, maps

# Create tables for demo (in a real app, use Alembic)
Base.metadata.create_all(bind=engine)

def seed_db():
    try:
        db = SessionLocal()
        if db.query(ExplorationTarget).count() == 0:
            targets_data = [
                {"name": "Zone Alpha-1", "description": "High reflectance anomaly in Band 4.", "latitude": 21.4312, "longitude": 79.8113, "prospectivity_score": 0.91, "is_verified": False},
                {"name": "Zone Alpha-2", "description": "Geological contact zone with potential outcroppings.", "latitude": 21.4322, "longitude": 79.8213, "prospectivity_score": 0.88, "is_verified": False},
                {"name": "Zone Beta-1", "description": "Terrain feature suggesting ancient riverbed.", "latitude": 21.1415, "longitude": 79.0815, "prospectivity_score": 0.75, "is_verified": True},
            ]
            for t in targets_data:
                db.add(ExplorationTarget(**t))
            db.commit()
        db.close()
    except Exception:
        # Silently skip seeding if the DB schema is stale (e.g. during tests
        # with an in-memory DB or a dev.db that needs migration).
        pass

seed_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Manganese Prospectivity Mapping API",
    version="1.0.0",
)

# CORS config
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
if not origins:
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "*"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if "*" not in origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(targets.router, prefix="/api/targets", tags=["targets"])
app.include_router(ml.router, prefix="/api/ml", tags=["ml"])
app.include_router(study_areas.router, prefix="/api/study-areas", tags=["study_areas"])
app.include_router(field_notes.router, prefix="/api/field-notes", tags=["field_notes"])
app.include_router(data_import.router, prefix="/api/data-import", tags=["data_import"])
app.include_router(maps.router, prefix="/api/maps", tags=["maps"])

@app.get("/")
def read_root():
    return {
        "project": settings.PROJECT_NAME,
        "mode": "DEMO MODE" if settings.DEMO_MODE else "PRODUCTION",
        "status": "online"
    }

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "mode": "demo"
    }