"""
Pydantic models for MongoDB candidate documents and API responses.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


# ------------------------------------------------------------------
# Extracted Data (from GeminiParser + rule-based)
# ------------------------------------------------------------------
class ExperienceEntry(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: List[str] = []


class EducationEntry(BaseModel):
    degree: Optional[str] = None
    university: Optional[str] = None
    year: Optional[str] = None


class ProjectEntry(BaseModel):
    project_name: Optional[str] = None
    site_name: Optional[str] = None
    role: Optional[str] = None
    responsibilities: List[str] = []
    duration_start: Optional[str] = None
    duration_end: Optional[str] = None


class ExtractedData(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio_urls: List[str] = []
    summary: Optional[str] = None
    experience: List[ExperienceEntry] = []
    education: List[EducationEntry] = []
    projects: List[ProjectEntry] = []
    skills: List[str] = []
    tools: List[str] = []
    certifications: List[str] = []
    discipline: Optional[str] = None
    position: Optional[str] = None
    confidence_score: int = 0
    status: str = "success"
    ai_enhanced: bool = False


# ------------------------------------------------------------------
# Computed Metrics (from ProfileEvaluator)
# ------------------------------------------------------------------
class SoftwareExperience(BaseModel):
    years: float = 0.0
    proficiency: str = "Basic"


class ComputedMetrics(BaseModel):
    total_experience_years: float = 0.0
    gcc_experience_years: float = 0.0
    seniority_level: str = "Junior"
    mnc_experience: bool = False
    software_experience: Dict[str, SoftwareExperience] = {}
    portfolio_relevancy_score: int = 0
    english_proficiency: str = "Intermediate"


# ------------------------------------------------------------------
# MongoDB Document
# ------------------------------------------------------------------
class CandidateDocument(BaseModel):
    filename: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    extracted_data: ExtractedData
    computed_metrics: ComputedMetrics


# ------------------------------------------------------------------
# API Response
# ------------------------------------------------------------------
class ProcessCVResponse(BaseModel):
    status: str
    filename: str
    candidate_id: Optional[str] = None
    extracted_data: Dict[str, Any] = {}
    computed_metrics: Dict[str, Any] = {}
