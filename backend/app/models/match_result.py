import uuid
from datetime import datetime
from sqlalchemy import Column, Float, Boolean, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class MatchResult(Base):
    """
    Represents the matching result between a candidate and a job description.
    Stores detailed scoring breakdown and explainable justification.
    """
    __tablename__ = "match_results"
    
    # Primary Key
    match_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.candidate_id"), nullable=False)
    jd_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.jd_id"), nullable=False)
    
    # Overall Score
    total_score = Column(Float, nullable=False, index=True)
    
    # Individual Component Scores
    skill_score = Column(Float, default=0.0, nullable=False)
    role_score = Column(Float, default=0.0, nullable=False)
    tool_score = Column(Float, default=0.0, nullable=False)
    experience_score = Column(Float, default=0.0, nullable=False)
    portfolio_score = Column(Float, default=0.0, nullable=False)
    quality_score = Column(Float, default=0.0, nullable=False)
    location_score = Column(Float, default=0.0, nullable=True)  # Optional
    
    # Detailed Breakdown (JSON with detailed calculations)
    score_breakdown = Column(JSON, nullable=True)
    
    # Explainable Justification
    justification = Column(Text, nullable=False)
    
    # Match Metadata
    matched_skills = Column(JSON, nullable=True)  # List of matched skills
    missing_skills = Column(JSON, nullable=True)  # List of missing must-have skills
    matched_tools = Column(JSON, nullable=True)  # List of matched tools
    
    # Status
    is_shortlisted = Column(Boolean, default=False, nullable=False)
    is_rejected = Column(Boolean, default=False, nullable=False)
    
    # CRM Sync
    crm_synced = Column(Boolean, default=False, nullable=False)
    crm_id = Column(String(255), nullable=True)  # External CRM reference
    crm_sync_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="match_results")
    job_description = relationship("JobDescription", back_populates="match_results")
    
    def __repr__(self):
        return f"<MatchResult {self.match_id} - Score: {self.total_score:.1f}>"
    
    @property
    def score_percentage(self) -> float:
        """Get score as percentage."""
        return self.total_score
