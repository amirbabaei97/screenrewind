import re
from sqlalchemy.orm import Session
from src.models.rule import Rule
from src.models.project import Project, Task
from src.core.ai import analyze_snapshot
from src.core.database import SessionLocal

def apply_rules(text_map: dict, db: Session):
    """
    Iterate through rules and apply regex patterns.
    text_map contains: {'window_title': ..., 'app_name': ..., 'ocr_text': ...}
    """
    rules = db.query(Rule).all()
    for rule in rules:
        field_value = text_map.get(rule.field, "")
        if not field_value:
            continue
            
        try:
            if re.search(rule.pattern, field_value, re.IGNORECASE):
                # Match found!
                # Fetch project and task names
                project = db.query(Project).filter(Project.id == rule.project_id).first()
                task = db.query(Task).filter(Task.id == rule.task_id).first()
                
                return {
                    "project": project.name if project else "Unknown",
                    "task": task.name if task else "General",
                    "explanation": f"Matched rule: {rule.name}"
                }
        except re.error:
            print(f"Invalid regex pattern in rule {rule.name}: {rule.pattern}")
            continue
            
    return None

def categorize_activity(image_path: str, ocr_text: str, window_title: str, app_name: str) -> dict:
    """
    Main entry point for categorization.
    Layer 1: Rules
    Layer 2: AI
    """
    db = SessionLocal()
    try:
        # Layer 1: Rules
        text_map = {
            "window_title": window_title,
            "app_name": app_name,
            "ocr_text": ocr_text
        }
        
        rule_result = apply_rules(text_map, db)
        if rule_result:
            return rule_result
            
        # Layer 2: AI
        # We pass the image path and OCR text to the AI
        return analyze_snapshot(image_path, ocr_text)
        
    finally:
        db.close()
