from sqlalchemy import create_engine
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
    Base.metadata.create_all(bind=engine)
