from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import snapshots
from src.core.database import init_db

app = FastAPI(title="ScreenRewind API")

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

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to ScreenRewind API"}
