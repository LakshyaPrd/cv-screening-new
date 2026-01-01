import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Candidate(Base):
    """
    Represents a candidate with extracted CV/portfolio data.
    Stores both raw OCR output and structured extracted information.
    """
    __tablename__ = "candidates"
    
    # Primary Key
    candidate_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.batch_id"), nullable=False)
    
    # Contact Information
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True, index=True)
    location = Column(String(255), nullable=True)
    
    # Personal Information (NEW)
    date_of_birth = Column(String(50), nullable=True)
    nationality = Column(String(100), nullable=True)
    marital_status = Column(String(50), nullable=True)
    military_status = Column(String(50), nullable=True)
    current_country = Column(String(100), nullable=True)
    current_city = Column(String(100), nullable=True)
    
    # Extended Contact Details (NEW)
    linkedin_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    behance_url = Column(String(500), nullable=True)
    
    # Position & Discipline Info (NEW)
    current_position = Column(String(255), nullable=True)
    discipline = Column(String(100), nullable=True)  # Architecture, Structural, MEP, etc.
    sub_discipline = Column(String(100), nullable=True)  # BIM Modeling, Coordination, etc.
    
    # Experience Metrics (NEW)
    total_experience_years = Column(Float, nullable=True)
    relevant_experience_years = Column(Float, nullable=True)
    gcc_experience_years = Column(Float, nullable=True)
    worked_on_gcc_projects = Column(String(10), default='false', nullable=True)  # Using string for SQLite compatibility
    worked_with_mncs = Column(String(10), default='false', nullable=True)  # Using string for SQLite compatibility
    
    # Salary & Availability (NEW)
    current_salary_aed = Column(Float, nullable=True)
    expected_salary_aed = Column(Float, nullable=True)
    notice_period_days = Column(Float, nullable=True)
    willing_to_relocate = Column(String(10), default='false', nullable=True)
    willing_to_travel = Column(String(10), default='false', nullable=True)
    
    # Evaluation Criteria (NEW)
    portfolio_relevancy_score = Column(Float, nullable=True)  # 0-100
    english_proficiency = Column(String(50), nullable=True)  # Basic/Good/Fluent/Native
    
    # Extracted Data (stored as JSON for flexibility)
    skills = Column(JSON, nullable=True)  # List of skills
    tools = Column(JSON, nullable=True)  # List of software/tools  
    education = Column(JSON, nullable=True)  # Basic education history (legacy)
    experience = Column(JSON, nullable=True)  # Basic work experience (legacy)
    portfolio_urls = Column(JSON, nullable=True)  # Portfolio links
    
    # Enhanced Structured Data (NEW)
    work_history = Column(JSON, nullable=True)  # Detailed work history with all fields
    software_experience = Column(JSON, nullable=True)  # Software with proficiency levels
    education_details = Column(JSON, nullable=True)  # Detailed education + certifications
    soft_skills = Column(JSON, nullable=True)  # List of soft skills
    
    # OCR Data
    raw_text = Column(Text, nullable=True)  # Full OCR output
    ocr_quality_score = Column(Float, nullable=True)  # 0-100 quality score
    
    # File References
    cv_file_path = Column(String(500), nullable=True)
    portfolio_file_path = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Processing status
    extraction_status = Column(String(50), default="pending", nullable=False)  # pending, completed, failed
    extraction_error = Column(Text, nullable=True)
    
    # Relationships
    batch = relationship("Batch", back_populates="candidates")
    match_results = relationship("MatchResult", back_populates="candidate", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Candidate {self.candidate_id} - {self.name or 'Unknown'}>"
    
    @property
    def is_complete(self) -> bool:
        """Check if candidate has minimum required information."""
        return bool(self.name and (self.email or self.phone))
