from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class JobDescriptionCreate(BaseModel):
    """Schema for creating a job description."""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    must_have_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)
    role_keywords: List[str] = Field(default_factory=list)
    location_preference: Optional[str] = Field(None, max_length=255)
    
    # Scoring weights (optional, will use defaults if not provided)
    skill_weight: Optional[int] = Field(40, ge=0, le=100)
    role_weight: Optional[int] = Field(20, ge=0, le=100)
    tool_weight: Optional[int] = Field(15, ge=0, le=100)
    experience_weight: Optional[int] = Field(15, ge=0, le=100)
    portfolio_weight: Optional[int] = Field(10, ge=0, le=100)
    quality_weight: Optional[int] = Field(5, ge=0, le=100)
    
    minimum_score_threshold: Optional[int] = Field(50, ge=0, le=100)
    
    @validator('skill_weight', 'role_weight', 'tool_weight', 'experience_weight', 'portfolio_weight', 'quality_weight')
    def validate_weights(cls, v):
        """Validate individual weights are reasonable."""
        if v < 0 or v > 100:
            raise ValueError("Weight must be between 0 and 100")
        return v
    
    @validator('quality_weight')
    def validate_total_weights(cls, v, values):
        """Validate total weights sum to 100."""
        total = (
            values.get('skill_weight', 0) +
            values.get('role_weight', 0) +
            values.get('tool_weight', 0) +
            values.get('experience_weight', 0) +
            values.get('portfolio_weight', 0) +
            v
        )
        if total != 100:
            raise ValueError(f"Total weights must sum to 100, got {total}")
        return v


class JobDescriptionUpdate(BaseModel):
    """Schema for updating a job description."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    must_have_skills: Optional[List[str]] = None
    nice_to_have_skills: Optional[List[str]] = None
    required_tools: Optional[List[str]] = None
    role_keywords: Optional[List[str]] = None
    location_preference: Optional[str] = None
    minimum_score_threshold: Optional[int] = Field(None, ge=0, le=100)


class JobDescriptionResponse(BaseModel):
    """Schema for job description response."""
    jd_id: UUID
    title: str
    description: str
    must_have_skills: List[str]
    nice_to_have_skills: List[str]
    required_tools: List[str]
    role_keywords: List[str]
    location_preference: Optional[str]
    skill_weight: int
    role_weight: int
    tool_weight: int
    experience_weight: int
    portfolio_weight: int
    quality_weight: int
    minimum_score_threshold: int
    is_active: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobDescriptionListResponse(BaseModel):
    """Schema for list of job descriptions."""
    job_descriptions: List[JobDescriptionResponse]
    total: int
