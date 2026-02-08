from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID


class ScoreBreakdown(BaseModel):
    """Detailed score breakdown."""
    skill_score: float
    role_score: float
    tool_score: float
    experience_score: float
    portfolio_score: float
    quality_score: float
    location_score: Optional[float] = 0.0


class MatchResultResponse(BaseModel):
    """Schema for match result response."""
    match_id: UUID
    candidate_id: UUID
    jd_id: UUID
    total_score: float
    skill_score: float
    role_score: float
    tool_score: float
    experience_score: float
    portfolio_score: float
    quality_score: float
    location_score: Optional[float]
    score_breakdown: Optional[Dict[str, Any]]
    justification: str
    matched_skills: Optional[List[str]]
    missing_skills: Optional[List[str]]
    matched_tools: Optional[List[str]]
    is_shortlisted: bool
    is_rejected: bool
    crm_synced: bool
    crm_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MatchResultWithCandidate(MatchResultResponse):
    """Match result with comprehensive candidate details."""
    # Basic Info
    candidate_name: Optional[str]
    candidate_email: Optional[str]
    candidate_phone: Optional[str]
    candidate_location: Optional[str]
    batch_id: Optional[UUID]  # NEW: Batch reference

    # Personal Information
    nationality: Optional[str]
    current_city: Optional[str]
    current_country: Optional[str]
    marital_status: Optional[str]

    # Position & Discipline
    current_position: Optional[str]
    discipline: Optional[str]
    sub_discipline: Optional[str]

    # Professional Summary
    summary: Optional[str]  # NEW: Professional summary from ATS parser

    # Experience Metrics
    total_experience_years: Optional[float]
    relevant_experience_years: Optional[float]
    gcc_experience_years: Optional[float]
    worked_on_gcc_projects: Optional[bool]
    worked_with_mncs: Optional[bool]

    # Work History (summary)
    work_history: Optional[List[Dict[str, Any]]]
    latest_company: Optional[str]
    latest_position: Optional[str]

    # Projects (NEW - structured project data)
    projects: Optional[List[Dict[str, Any]]]

    # Skills & Tools
    skills: Optional[List[str]]  # NEW: All extracted skills
    tools: Optional[List[str]]  # NEW: All extracted tools
    software_experience: Optional[List[Dict[str, Any]]]
    top_software: Optional[List[str]]

    # Education & Certifications
    education_details: Optional[List[Dict[str, Any]]]
    highest_degree: Optional[str]
    certifications: Optional[List[str]]  # NEW: Certifications

    # Salary & Availability
    expected_salary_aed: Optional[float]
    notice_period_days: Optional[int]
    willing_to_relocate: Optional[bool]
    willing_to_travel: Optional[bool]

    # Evaluation
    portfolio_relevancy_score: Optional[float]
    english_proficiency: Optional[str]
    soft_skills: Optional[List[str]]

    # Links
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    portfolio_urls: Optional[List[str]]  # NEW: All portfolio URLs
    behance_url: Optional[str]


class MatchListResponse(BaseModel):
    """Schema for list of match results."""
    matches: List[MatchResultWithCandidate]
    total: int
    total_pages: int
    current_page: int


class ShortlistRequest(BaseModel):
    """Schema for bulk shortlist/reject."""
    match_ids: List[UUID] = Field(..., min_items=1)


class MatchFilters(BaseModel):
    """Schema for filtering match results."""
    min_score: Optional[float] = Field(None, ge=0, le=100)
    must_have_skills: Optional[List[str]] = None
    required_tools: Optional[List[str]] = None
    location: Optional[str] = None
    is_shortlisted: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
