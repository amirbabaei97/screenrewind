from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import snapshots, analytics, projects, rules, system
from src.core.database import init_db
from src.core.security import get_api_key
from fastapi import Security, Depends

app = FastAPI(
    title="ScreenRewind API",
    dependencies=[Security(get_api_key)]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(snapshots.router)
app.include_router(analytics.router)
# app.include_router(categories.router) # Deprecated in favor of projects/rules
app.include_router(projects.router)
app.include_router(rules.router)
app.include_router(system.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to ScreenRewind API"}
