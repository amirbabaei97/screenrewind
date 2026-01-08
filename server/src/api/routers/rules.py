from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.models.rule import Rule
from src.schemas.categorization import RuleCreate, Rule as RuleSchema

router = APIRouter(
    prefix="/rules",
    tags=["rules"]
)

@router.get("/", response_model=List[RuleSchema])
def read_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rules = db.query(Rule).offset(skip).limit(limit).all()
    return rules

@router.post("/", response_model=RuleSchema)
def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    new_rule = Rule(
        name=rule.name,
        pattern=rule.pattern,
        field=rule.field,
        project_id=rule.project_id,
        task_id=rule.task_id
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return new_rule

@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"ok": True}
