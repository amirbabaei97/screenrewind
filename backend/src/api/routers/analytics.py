from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Dict

from src.core.database import get_db
from src.models.snapshot import Snapshot

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)

@router.get("/time-distribution")
def get_time_distribution(
    start_date: datetime = Query(..., example="2026-01-01T00:00:00"),
    end_date: datetime = Query(..., example="2026-01-02T23:59:59"),
    db: Session = Depends(get_db)
):
    """
    Calculate time spent per category based on snapshot count.
    Assumes 1 snapshot = 10 seconds (default interval).
    """
    # Group by category and count
    results = db.query(
        Snapshot.category, 
        func.count(Snapshot.id).label("count")
    ).filter(
        Snapshot.timestamp >= start_date,
        Snapshot.timestamp <= end_date
    ).group_by(Snapshot.category).all()
    
    # Convert to time (minutes)
    # 1 snapshot = 10 seconds
    # minutes = count * 10 / 60 = count / 6
    
    distribution = {}
    total_minutes = 0
    
    for category, count in results:
        minutes = round(count * 10 / 60, 2)
        distribution[category] = minutes
        total_minutes += minutes
        
    return {
        "period": {
            "start": start_date,
            "end": end_date
        },
        "total_minutes": total_minutes,
        "distribution": distribution
    }
