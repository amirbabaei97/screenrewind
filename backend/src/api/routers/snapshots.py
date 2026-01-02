from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.core.database import get_db
from src.models.snapshot import Snapshot
from src.schemas.snapshot import SnapshotResponse

router = APIRouter(
    prefix="/snapshots",
    tags=["snapshots"]
)

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
