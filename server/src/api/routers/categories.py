from fastapi import APIRouter, HTTPException, Body
from typing import Dict, List
import json

from src.core.config import load_categories, save_categories

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get("/", response_model=Dict[str, List[str]])
def get_categories():
    """Get the current category configuration."""
    return load_categories()

@router.post("/")
def update_categories(categories: Dict[str, List[str]] = Body(...)):
    """Update the category configuration."""
    try:
        save_categories(categories)
        return {"message": "Categories updated successfully", "categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
