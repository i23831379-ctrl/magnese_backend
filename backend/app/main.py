from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import maps, manganese, targets

app = FastAPI(title="MANGANEX AI API", version="1.0.0", description="AI-assisted manganese prospectivity demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(targets.router, prefix="/api")
app.include_router(maps.router, prefix="/api")
app.include_router(manganese.router, prefix="/api")

@app.get("/")
def root():
    return {"name": "MANGANEX AI API", "status": "online"}

@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "demo"}
