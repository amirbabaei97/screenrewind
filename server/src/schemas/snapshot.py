from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SnapshotBase(BaseModel):
    file_path: str
    ocr_text: Optional[str] = None
    window_title: Optional[str] = None
    app_name: Optional[str] = None
    project_name: Optional[str] = None
    task_name: Optional[str] = None
    explanation: Optional[str] = None

class SnapshotCreate(SnapshotBase):
    pass

class SnapshotResponse(SnapshotBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
