from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ubuntu:password@localhost/screenrewind")

engine = create_engine(DATABASE_URL)
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
