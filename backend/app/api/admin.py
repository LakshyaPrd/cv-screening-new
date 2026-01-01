from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.config import settings

router = APIRouter()


@router.get("/admin/skills")
async def get_skills_dictionary():
    """
    Get the current skills dictionary.
    """
    # In production, this would be loaded from database or config file
    from app.services.dictionaries import get_skills_dict
    return {"skills": get_skills_dict()}


@router.post("/admin/skills")
async def update_skills_dictionary(skills: List[str]):
    """
    Update the skills dictionary.
    """
    # In production, save to database
    return {"message": "Skills dictionary updated", "count": len(skills)}


@router.get("/admin/tools")
async def get_tools_dictionary():
    """
    Get the current tools/software dictionary.
    """
    from app.services.dictionaries import get_tools_dict
    return {"tools": get_tools_dict()}


@router.post("/admin/tools")
async def update_tools_dictionary(tools: List[str]):
    """
    Update the tools dictionary.
    """
    return {"message": "Tools dictionary updated", "count": len(tools)}


@router.get("/admin/scoring-weights")
async def get_scoring_weights():
    """
    Get current default scoring weights.
    """
    return {
        "skill_weight": settings.DEFAULT_SKILL_WEIGHT,
        "role_weight": settings.DEFAULT_ROLE_WEIGHT,
        "tool_weight": settings.DEFAULT_TOOL_WEIGHT,
        "experience_weight": settings.DEFAULT_EXPERIENCE_WEIGHT,
        "portfolio_weight": settings.DEFAULT_PORTFOLIO_WEIGHT,
        "quality_weight": settings.DEFAULT_QUALITY_WEIGHT,
    }


@router.put("/admin/scoring-weights")
async def update_scoring_weights(weights: Dict[str, int]):
    """
    Update default scoring weights.
    """
    # Validate weights sum to 100
    total = sum(weights.values())
    if total != 100:
        raise HTTPException(
            status_code=400,
            detail=f"Weights must sum to 100, got {total}"
        )
    
    # In production, update config or database
    return {"message": "Scoring weights updated", "weights": weights}


@router.get("/admin/system-health")
async def get_system_health(db: Session = Depends(get_db)):
    """
    Get system health metrics.
    """
    from app.models.batch import Batch
    from app.models.candidate import Candidate
    from app.models.match_result import MatchResult
    
    # Get counts
    total_batches = db.query(Batch).count()
    total_candidates = db.query(Candidate).count()
    total_matches = db.query(MatchResult).count()
    
    # Get processing status
    from app.models.batch import BatchStatus
    processing_batches = db.query(Batch).filter(
        Batch.status == BatchStatus.PROCESSING
    ).count()
    
    return {
        "status": "healthy",
        "metrics": {
            "total_batches": total_batches,
            "processing_batches": processing_batches,
            "total_candidates": total_candidates,
            "total_matches": total_matches,
        }
    }


@router.get("/admin/ocr-config")
async def get_ocr_config():
    """
    Get OCR configuration.
    """
    return {
        "dpi": settings.OCR_DPI,
        "languages": settings.OCR_LANGUAGES,
        "tesseract_path": settings.TESSERACT_PATH,
    }
