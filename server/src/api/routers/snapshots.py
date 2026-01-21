from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import shutil
import os
import uuid

from src.core.database import get_db
from src.models.snapshot import Snapshot
from src.schemas.snapshot import SnapshotResponse
from src.core.categorization import categorize_activity
from src.core.config import load_settings, DEFAULT_SETTINGS

router = APIRouter(
    prefix="/snapshots",
    tags=["snapshots"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=SnapshotResponse)
def create_snapshot(
    file: UploadFile = File(...),
    ocr_text: str = Form(""),
    window_title: str = Form(""),
    app_name: str = Form(""),
    timestamp_str: str = Form(..., alias="timestamp"), # Expecting ISO string
    db: Session = Depends(get_db)
):
    # 1. Save Screenshot
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert timestamp
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
    except ValueError:
        timestamp = datetime.now()

    # 2. Categorization (Layer 1 & 2)
    # Note: categorize_activity currently creates its own session, we should probably refactor it to accept db session
    # For now, we will trust it or ideally passing db helps transaction management
    # Let's import the logic directly if needed or update the function.
    # But for now, let's just call it. Note: image_path might be needed for AI if it looks at the image.
    
    category_result = categorize_activity(file_path, ocr_text, window_title, app_name)
    
    project_name = category_result.get("project", "Uncategorized")
    task_name = category_result.get("task", "General")
    
    # 3. Save to DB
    settings = load_settings()
    duration = settings.get("capture_interval", DEFAULT_SETTINGS["capture_interval"])

    new_snapshot = Snapshot(
        timestamp=timestamp,
        file_path=file_path,
        ocr_text=ocr_text,
        window_title=window_title,
        app_name=app_name,
        # We might need to store project/task on the snapshot model if we want to query it later
        project_name=project_name,
        task_name=task_name,
        explanation=category_result.get("explanation", ""),
        duration_seconds=int(duration)
    )
    
    # Check if Snapshot model has project_id/task_id, if so update them
    # For now, just save basic info
    
    db.add(new_snapshot)
    db.commit()
    db.refresh(new_snapshot)
    
    return new_snapshot

@router.get("/", response_model=List[SnapshotResponse])
def get_snapshots(
    skip: int = 0, 
    limit: int = 100, 
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Snapshot)
    if q:
        query = query.filter(Snapshot.ocr_text.contains(q))
    return query.order_by(Snapshot.timestamp.desc()).offset(skip).limit(limit).all()

@router.get("/latest", response_model=SnapshotResponse)
def get_latest_snapshot(db: Session = Depends(get_db)):
    snapshot = db.query(Snapshot).order_by(Snapshot.timestamp.desc()).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshots found")
    return snapshot

@router.get("/{snapshot_id}", response_model=SnapshotResponse)
def get_snapshot(snapshot_id: int, db: Session = Depends(get_db)):
    snapshot = db.query(Snapshot).filter(Snapshot.id == snapshot_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snapshot
