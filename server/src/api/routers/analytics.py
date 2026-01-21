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

@router.get("/projects")
def get_project_distribution(
    start: datetime,
    end: datetime,
    db: Session = Depends(get_db)
):
    """
    Get time distribution by project.
    """
    results = db.query(
        Snapshot.project_name,
        func.sum(Snapshot.duration_seconds).label("total_seconds")
    ).filter(
        Snapshot.timestamp >= start,
        Snapshot.timestamp <= end
    ).group_by(Snapshot.project_name).all()
    
    data = []
    total_seconds = sum(r[1] for r in results) if results else 0
    
    for project, seconds in results:
        minutes = round(seconds / 60, 2)
        project_name = project if project else "Uncategorized"
        data.append({
            "name": project_name,
            "value": minutes,
            "percentage": round((seconds / total_seconds) * 100, 1) if total_seconds > 0 else 0
        })
        
    return data

@router.get("/projects/{project_name}/tasks")
def get_task_distribution(
    project_name: str,
    start: datetime,
    end: datetime,
    db: Session = Depends(get_db)
):
    """
    Get time distribution by task for a specific project.
    """
    results = db.query(
        Snapshot.task_name,
        func.sum(Snapshot.duration_seconds).label("total_seconds")
    ).filter(
        Snapshot.timestamp >= start,
        Snapshot.timestamp <= end,
        Snapshot.project_name == project_name
    ).group_by(Snapshot.task_name).all()
    
    data = []
    total_seconds = sum(r[1] for r in results) if results else 0
    
    for task, seconds in results:
        minutes = round(seconds / 60, 2)
        task_name = task if task else "General"
        data.append({
            "name": task_name,
            "value": minutes,
            "percentage": round((seconds / total_seconds) * 100, 1) if total_seconds > 0 else 0
        })
        
    return data
