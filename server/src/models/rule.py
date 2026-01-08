from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base
from datetime import datetime

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    pattern = Column(String, nullable=False)  # Regex or exact match string
    field = Column(String, nullable=False)    # "app_name" or "window_title"
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    
    # Relationships
    project = relationship("Project")
    task = relationship("Task")

    def __repr__(self):
        return f"<Rule(name={self.name}, pattern={self.pattern})>"
