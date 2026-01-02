from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from src.core.database import Base

class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    file_path = Column(String, nullable=False)
    ocr_text = Column(Text, nullable=True)
    window_title = Column(String, nullable=True)
    app_name = Column(String, nullable=True)
    category = Column(String, default="Uncategorized")
    
    def __repr__(self):
        return f"<Snapshot(id={self.id}, timestamp={self.timestamp})>"
