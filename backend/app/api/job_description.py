from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.job_description import JobDescription
from app.schemas.job_description import (
    JobDescriptionCreate,
    JobDescriptionUpdate,
    JobDescriptionResponse,
    JobDescriptionListResponse,
)

router = APIRouter()


@router.post("/jd", response_model=JobDescriptionResponse, status_code=201)
async def create_job_description(
    jd: JobDescriptionCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new job description with requirements and scoring weights.
    """
    # Create JD
    new_jd = JobDescription(
        title=jd.title,
        description=jd.description,
        must_have_skills=jd.must_have_skills,
        nice_to_have_skills=jd.nice_to_have_skills,
        required_tools=jd.required_tools,
        role_keywords=jd.role_keywords,
        location_preference=jd.location_preference,
        skill_weight=jd.skill_weight,
        role_weight=jd.role_weight,
        tool_weight=jd.tool_weight,
        experience_weight=jd.experience_weight,
        portfolio_weight=jd.portfolio_weight,
        quality_weight=jd.quality_weight,
        minimum_score_threshold=jd.minimum_score_threshold,
    )
    
    db.add(new_jd)
    db.commit()
    db.refresh(new_jd)
    
    return JobDescriptionResponse.from_orm(new_jd)


@router.get("/jd/{jd_id}", response_model=JobDescriptionResponse)
async def get_job_description(
    jd_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve a job description by ID.
    """
    jd = db.query(JobDescription).filter(JobDescription.jd_id == jd_id).first()
    
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    return JobDescriptionResponse.from_orm(jd)


@router.put("/jd/{jd_id}", response_model=JobDescriptionResponse)
async def update_job_description(
    jd_id: UUID,
    jd_update: JobDescriptionUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a job description.
    """
    jd = db.query(JobDescription).filter(JobDescription.jd_id == jd_id).first()
    
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Update fields
    update_data = jd_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(jd, field, value)
    
    db.commit()
    db.refresh(jd)
    
    return JobDescriptionResponse.from_orm(jd)


@router.get("/jds", response_model=JobDescriptionListResponse)
async def list_job_descriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: bool = True,
    db: Session = Depends(get_db),
):
    """
    List all job descriptions.
    """
    query = db.query(JobDescription)
    
    if is_active:
        query = query.filter(JobDescription.is_active == 1)
    
    query = query.order_by(JobDescription.created_at.desc())
    
    jds = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return JobDescriptionListResponse(
        job_descriptions=[JobDescriptionResponse.from_orm(jd) for jd in jds],
        total=total,
    )


@router.delete("/jd/{jd_id}", status_code=204)
async def delete_job_description(
    jd_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete (archive) a job description.
    """
    jd = db.query(JobDescription).filter(JobDescription.jd_id == jd_id).first()
    
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Soft delete by marking inactive
    jd.is_active = 0
    db.commit()
    
    return None
