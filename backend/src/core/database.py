from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from src.core.config import APP_DATA_DIR

# Ensure the data directory exists
DB_DIR = os.path.join(APP_DATA_DIR, "data")
os.makedirs(DB_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'screenrewind.db')}"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import all models so Base.metadata knows about them
    from src.models.snapshot import Snapshot
    from src.models.project import Project, Task
    from src.models.rule import Rule
    
    Base.metadata.create_all(bind=engine)
    
    # Simple migration to add new columns to snapshots if they don't exist
    # This is a hacky migration for SQLite since we don't have Alembic set up yet
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE snapshots ADD COLUMN project_name VARCHAR"))
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE snapshots ADD COLUMN task_name VARCHAR"))
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE snapshots ADD COLUMN explanation TEXT"))
        except Exception:
            pass
