from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Nested models for structured data
class WorkHistoryItem(BaseModel):
    """Detailed work history entry."""
    job_title: str
    seniority_level: Optional[str] = None  # Junior/Mid-Level/Senior/Lead/Manager/Director
    company_name: Optional[str] = None
    company_location: Optional[str] = None  # City, Country
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_months: Optional[int] = None
    mode_of_work: Optional[str] = None  # On-site/Remote/Hybrid/Flexible
    roles_responsibilities: Optional[str] = None
    key_projects: Optional[List[str]] = []
    project_locations: Optional[List[str]] = []  # Local or GCC


class SoftwareExperience(BaseModel):
    """Software/tool proficiency."""
    software_name: str
    years_of_experience: Optional[float] = None
    proficiency_level: Optional[str] = None  # Basic/Intermediate/Expert
    is_relevant: Optional[bool] = True


class EducationDetail(BaseModel):
    """Detailed education information."""
    degree: str
    major: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[str] = None
    relevant_qualification: Optional[bool] = None
    certifications: Optional[List[str]] = []


class CandidateBase(BaseModel):
    """Base candidate schema with all fields."""
    # Contact Information
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    
    # Personal Information
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[str] = None
    military_status: Optional[str] = None
    current_country: Optional[str] = None
    current_city: Optional[str] = None
    
    # Extended Contact
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    behance_url: Optional[str] = None
    
    # Position & Discipline
    current_position: Optional[str] = None
    discipline: Optional[str] = None
    sub_discipline: Optional[str] = None
    
    # Experience Metrics
    total_experience_years: Optional[float] = None
    relevant_experience_years: Optional[float] = None
    gcc_experience_years: Optional[float] = None
    worked_on_gcc_projects: Optional[bool] = None
    worked_with_mncs: Optional[bool] = None
    
    # Salary & Availability
    current_salary_aed: Optional[float] = None
    expected_salary_aed: Optional[float] = None
    notice_period_days: Optional[int] = None
    willing_to_relocate: Optional[bool] = None
    willing_to_travel: Optional[bool] = None
    
    # Evaluation
    portfolio_relevancy_score: Optional[float] = None
    english_proficiency: Optional[str] = None


class CandidateCreate(CandidateBase):
    """Schema for creating a candidate."""
    batch_id: UUID
    
    # Legacy fields
    skills: Optional[List[str]] = []
    tools: Optional[List[str]] = []
    education: Optional[List[Dict[str, Any]]] = []
    experience: Optional[List[Dict[str, Any]]] = []
    portfolio_urls: Optional[List[str]] = []
    
    # Enhanced fields
    work_history: Optional[List[Dict[str, Any]]] = []
    software_experience: Optional[List[Dict[str, Any]]] = []
    education_details: Optional[List[Dict[str, Any]]] = []
    soft_skills: Optional[List[str]] = []


class CandidateResponse(CandidateBase):
    """Schema for candidate response with all comprehensive data."""
    candidate_id: UUID
    batch_id: UUID
    
    # Legacy fields (for backward compatibility)
    skills: Optional[List[str]]
    tools: Optional[List[str]]
    education: Optional[List[Dict[str, Any]]]
    experience: Optional[List[Dict[str, Any]]]
    portfolio_urls: Optional[List[str]]
    
    # Enhanced structured fields
    work_history: Optional[List[Dict[str, Any]]]
    software_experience: Optional[List[Dict[str, Any]]]
    education_details: Optional[List[Dict[str, Any]]]
    soft_skills: Optional[List[str]]
    
    # Metadata
    ocr_quality_score: Optional[float]
    extraction_status: str
    cv_file_path: Optional[str]
    portfolio_file_path: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CandidateListResponse(BaseModel):
    """Schema for list of candidates."""
    candidates: List[CandidateResponse]
    total: int


class CandidateDetailedView(BaseModel):
    """Comprehensive candidate view for tabular display."""
    candidate_id: UUID
    
    # Personal & Contact
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    nationality: Optional[str]
    current_city: Optional[str]
    current_country: Optional[str]
    
    # Position & Experience
    current_position: Optional[str]
    discipline: Optional[str]
    sub_discipline: Optional[str]
    total_experience_years: Optional[float]
    relevant_experience_years: Optional[float]
    gcc_experience_years: Optional[float]
    worked_on_gcc_projects: Optional[bool]
    worked_with_mncs: Optional[bool]
    
    # Work History
    work_history: Optional[List[WorkHistoryItem]]
    
    # Software Skills
    software_experience: Optional[List[SoftwareExperience]]
    top_software: Optional[List[str]] = []  # Top 5 relevant software
    
    # Education
    education_details: Optional[List[EducationDetail]]
    
    # Salary & Availability
    expected_salary_aed: Optional[float]
    notice_period_days: Optional[int]
    willing_to_relocate: Optional[bool]
    
    # Evaluation
    portfolio_relevancy_score: Optional[float]
    english_proficiency: Optional[str]
    soft_skills: Optional[List[str]]
    
    # Links
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    
    class Config:
        from_attributes = True
