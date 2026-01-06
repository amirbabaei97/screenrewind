from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.models.snapshot import Snapshot

router = APIRouter(
    prefix="/system",
    tags=["system"]
)

@router.delete("/reset-data")
def reset_data(db: Session = Depends(get_db)):
    """
    Deletes all recorded snapshots and associated data (OCR, explanations).
    Does NOT delete Projects, Tasks, or Rules.
    """
    try:
        # Delete all rows from snapshots table
        # Since ocr_text etc are columns in snapshots, they are deleted too.
        # If there were separate tables for OCR/Embeddings linked by FK, we'd delete them too 
        # (or cascade handles it). 
        # Currently Snapshot model has these as columns.
        db.query(Snapshot).delete()
        db.commit()
        return {"status": "success", "message": "All snapshot data cleared"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
