import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class JobDescription(Base):
    """
    Represents a job description with requirements and scoring weights.
    Used for matching candidates against job requirements.
    """
    __tablename__ = "job_descriptions"
    
    # Primary Key
    jd_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic Info
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Requirements (stored as JSON arrays)
    must_have_skills = Column(JSON, nullable=False, default=list)
    nice_to_have_skills = Column(JSON, nullable=True, default=list)
    required_tools = Column(JSON, nullable=True, default=list)
    role_keywords = Column(JSON, nullable=True, default=list)
    location_preference = Column(String(255), nullable=True)
    
    # Scoring Weights (must sum to 100)
    skill_weight = Column(Integer, default=40, nullable=False)
    role_weight = Column(Integer, default=20, nullable=False)
    tool_weight = Column(Integer, default=15, nullable=False)
    experience_weight = Column(Integer, default=15, nullable=False)
    portfolio_weight = Column(Integer, default=10, nullable=False)
    quality_weight = Column(Integer, default=5, nullable=False)
    
    # Additional Configuration
    minimum_score_threshold = Column(Integer, default=50, nullable=False)
    
    # Metadata
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)  # 1=active, 0=archived
    
    # Relationships
    match_results = relationship("MatchResult", back_populates="job_description", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<JobDescription {self.jd_id} - {self.title}>"
    
    @property
    def total_weight(self) -> int:
        """Calculate total weight (should be 100)."""
        return (
            self.skill_weight +
            self.role_weight +
            self.tool_weight +
            self.experience_weight +
            self.portfolio_weight +
            self.quality_weight
        )
    
    def validate_weights(self) -> bool:
        """Validate that weights sum to 100."""
        return self.total_weight == 100
