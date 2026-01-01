from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.batch import Batch
from app.schemas.batch import BatchResponse, BatchDetailResponse, BatchListResponse
from app.schemas.candidate import CandidateListResponse, CandidateResponse

router = APIRouter()


@router.get("/batch/{batch_id}", response_model=BatchDetailResponse)
async def get_batch(
    batch_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get batch details by ID including processing status.
    """
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return BatchDetailResponse.from_orm(batch)


@router.get("/batch/{batch_id}/candidates", response_model=CandidateListResponse)
async def get_batch_candidates(
    batch_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get all candidates from a specific batch.
    """
    # Check batch exists
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Get candidates
    from app.models.candidate import Candidate
    
    candidates = (
        db.query(Candidate)
        .filter(Candidate.batch_id == batch_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    total = db.query(Candidate).filter(Candidate.batch_id == batch_id).count()
    
    return CandidateListResponse(
        candidates=[CandidateResponse.from_orm(c) for c in candidates],
        total=total,
    )


@router.get("/batches", response_model=BatchListResponse)
async def list_batches(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List all batches with optional filtering by user.
    """
    query = db.query(Batch)
    
    if user_id:
        query = query.filter(Batch.user_id == user_id)
    
    query = query.order_by(Batch.created_at.desc())
    
    batches = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return BatchListResponse(
        batches=[BatchResponse.from_orm(b) for b in batches],
        total=total,
    )


@router.delete("/batch/{batch_id}", status_code=204)
async def delete_batch(
    batch_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a batch and all associated candidates.
    """
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Delete associated files
    import shutil
    from pathlib import Path
    batch_dir = Path(settings.UPLOAD_DIR) / str(batch_id)
    if batch_dir.exists():
        shutil.rmtree(batch_dir)
    
    # Delete from database (cascade will delete candidates)
    db.delete(batch)
    db.commit()
    
    return None
