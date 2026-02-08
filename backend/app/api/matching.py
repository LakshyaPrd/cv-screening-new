from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.job_description import JobDescription
from app.models.candidate import Candidate
from app.models.match_result import MatchResult
from app.schemas.match import (
    MatchResultResponse,
    MatchResultWithCandidate,
    MatchListResponse,
    ShortlistRequest,
    MatchFilters,
)

router = APIRouter()


@router.post("/jd/{jd_id}/match", status_code=202)
async def match_candidates_to_jd(
    jd_id: UUID,
    background_tasks: BackgroundTasks,
    batch_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    """
    Match candidates against a job description.
    If batch_id is provided, only matches candidates from that batch.
    Otherwise, matches all candidates.
    """
    # Verify JD exists
    jd = db.query(JobDescription).filter(JobDescription.jd_id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Queue matching task
    background_tasks.add_task(
        run_matching_task,
        jd_id=str(jd_id),
        batch_id=str(batch_id) if batch_id else None,
    )
    
    return {
        "message": "Matching process started",
        "jd_id": str(jd_id),
        "status_url": f"/api/jd/{jd_id}/matches"
    }


@router.get("/jd/{jd_id}/matches", response_model=MatchListResponse)
async def get_matched_candidates(
    jd_id: UUID,
    batch_id: Optional[UUID] = Query(None, description="Filter by specific batch"),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    is_shortlisted: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get ranked candidates for a job description with optional filtering.
    Can filter by batch_id to show only candidates from a specific batch.
    """
    # Build query
    query = (
        db.query(MatchResult, Candidate)
        .join(Candidate, MatchResult.candidate_id == Candidate.candidate_id)
        .filter(MatchResult.jd_id == jd_id)
    )

    # Apply filters
    if batch_id is not None:
        query = query.filter(Candidate.batch_id == batch_id)

    if min_score is not None:
        query = query.filter(MatchResult.total_score >= min_score)

    if is_shortlisted is not None:
        query = query.filter(MatchResult.is_shortlisted == is_shortlisted)
    
    # Order by score descending
    query = query.order_by(MatchResult.total_score.desc())
    
    # Pagination
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    skip = (page - 1) * page_size
    
    results = query.offset(skip).limit(page_size).all()
    
    # Format response with ALL comprehensive candidate data
    matches = []
    for match_result, candidate in results:
        # Helper to convert string boolean to actual boolean
        def to_bool(val):
            if isinstance(val, str):
                return val.lower() == 'true'
            return bool(val) if val else False
        
        # Extract summary fields
        latest_company = None
        latest_position = None
        if candidate.work_history and len(candidate.work_history) > 0:
            latest_company = candidate.work_history[0].get('company_name')
            latest_position = candidate.work_history[0].get('job_title')
        
        top_software = []
        if candidate.software_experience:
            top_software = [sw.get('software_name') for sw in candidate.software_experience[:5]]
        
        highest_degree = None
        if candidate.education_details and len(candidate.education_details) > 0:
            highest_degree = candidate.education_details[0].get('degree')
        
        match_data = MatchResultWithCandidate(
            # Match scores
            match_id=match_result.match_id,
            jd_id=match_result.jd_id,
            candidate_id=match_result.candidate_id,
            total_score=match_result.total_score,
            skill_score=match_result.skill_score,
            role_score=match_result.role_score,
            tool_score=match_result.tool_score,
            experience_score=match_result.experience_score,
            portfolio_score=match_result.portfolio_score,
            quality_score=match_result.quality_score,
            location_score=match_result.location_score or 0.0,
            score_breakdown=match_result.score_breakdown or {},
            matched_skills=match_result.matched_skills or [],
            missing_skills=match_result.missing_skills or [],
            matched_tools=match_result.matched_tools or [],
            justification=match_result.justification or "",
            is_shortlisted=match_result.is_shortlisted,
            is_rejected=match_result.is_rejected,
            crm_synced=match_result.crm_synced,
            crm_id=match_result.crm_id,
            created_at=match_result.created_at,

            # Basic candidate info
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            candidate_phone=candidate.phone,
            candidate_location=candidate.location,
            batch_id=candidate.batch_id,  # NEW

            # Personal Information
            nationality=candidate.nationality,
            current_city=candidate.current_city,
            current_country=candidate.current_country,
            marital_status=candidate.marital_status,

            # Position & Discipline
            current_position=candidate.current_position,
            discipline=candidate.discipline,
            sub_discipline=candidate.sub_discipline,

            # Professional Summary (NEW)
            summary=candidate.experience[0].get('description') if candidate.experience and len(candidate.experience) > 0 else None,

            # Experience Metrics
            total_experience_years=candidate.total_experience_years,
            relevant_experience_years=candidate.relevant_experience_years,
            gcc_experience_years=candidate.gcc_experience_years,
            worked_on_gcc_projects=to_bool(candidate.worked_on_gcc_projects),
            worked_with_mncs=to_bool(candidate.worked_with_mncs),

            # Work History
            work_history=candidate.work_history,
            latest_company=latest_company,
            latest_position=latest_position,

            # Projects (NEW - structured project data)
            projects=candidate.projects or [],

            # Skills & Tools (NEW)
            skills=candidate.skills or [],
            tools=candidate.tools or [],
            software_experience=candidate.software_experience,
            top_software=top_software,

            # Education & Certifications
            education_details=candidate.education_details,
            highest_degree=highest_degree,
            certifications=candidate.education_details[0].get('certifications', []) if candidate.education_details and len(candidate.education_details) > 0 else [],

            # Salary & Availability
            expected_salary_aed=candidate.expected_salary_aed,
            notice_period_days=candidate.notice_period_days,
            willing_to_relocate=to_bool(candidate.willing_to_relocate),
            willing_to_travel=to_bool(candidate.willing_to_travel),

            # Evaluation
            portfolio_relevancy_score=candidate.portfolio_relevancy_score,
            english_proficiency=candidate.english_proficiency,
            soft_skills=candidate.soft_skills,

            # Links
            linkedin_url=candidate.linkedin_url,
            portfolio_url=candidate.portfolio_url,
            portfolio_urls=candidate.portfolio_urls or [],  # NEW
            behance_url=candidate.behance_url,
        )
        matches.append(match_data)
    
    return MatchListResponse(
        matches=matches,
        total=total,
        total_pages=total_pages,
        current_page=page,
    )


@router.post("/jd/{jd_id}/shortlist", status_code=200)
async def shortlist_candidates(
    jd_id: UUID,
    request: ShortlistRequest,
    db: Session = Depends(get_db),
):
    """
    Bulk shortlist candidates.
    """
    # Update match results
    updated = (
        db.query(MatchResult)
        .filter(
            MatchResult.jd_id == jd_id,
            MatchResult.match_id.in_(request.match_ids)
        )
        .update({MatchResult.is_shortlisted: True}, synchronize_session=False)
    )
    
    db.commit()
    
    return {"message": f"Shortlisted {updated} candidates"}


@router.post("/jd/{jd_id}/reject", status_code=200)
async def reject_candidates(
    jd_id: UUID,
    request: ShortlistRequest,
    db: Session = Depends(get_db),
):
    """
    Bulk reject candidates.
    """
    # Update match results
    updated = (
        db.query(MatchResult)
        .filter(
            MatchResult.jd_id == jd_id,
            MatchResult.match_id.in_(request.match_ids)
        )
        .update({MatchResult.is_rejected: True}, synchronize_session=False)
    )
    
    db.commit()
    
    return {"message": f"Rejected {updated} candidates"}


def run_matching_task(jd_id: str, batch_id: Optional[str] = None):
    """
    Background task to run matching algorithm.
    """
    from app.services.matcher import CandidateMatcher
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Get JD
        jd = db.query(JobDescription).filter(JobDescription.jd_id == jd_id).first()
        if not jd:
            return
        
        # Get candidates
        query = db.query(Candidate).filter(Candidate.extraction_status == "completed")
        if batch_id:
            query = query.filter(Candidate.batch_id == batch_id)
        
        candidates = query.all()
        
        # Delete existing match results for this JD to avoid duplicates
        existing_matches = db.query(MatchResult).filter(MatchResult.jd_id == jd_id)
        if batch_id:
            # Only delete matches for candidates in this batch
            candidate_ids = [c.candidate_id for c in candidates]
            existing_matches = existing_matches.filter(MatchResult.candidate_id.in_(candidate_ids))
        
        deleted_count = existing_matches.delete(synchronize_session=False)
        db.commit()
        print(f"Deleted {deleted_count} existing match results")
        
        # Run matching
        matcher = CandidateMatcher()
        for candidate in candidates:
            try:
                result = matcher.match_candidate(candidate, jd, db)
                db.add(result)
                db.commit()
            except Exception as e:
                print(f"Error matching candidate {candidate.candidate_id}: {e}")
                continue
                
    finally:
        db.close()
