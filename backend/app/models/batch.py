import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class BatchStatus(str, enum.Enum):
    """Batch processing status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Batch(Base):
    """
    Represents a batch of uploaded CVs/portfolios.
    Tracks the processing status and progress.
    """
    __tablename__ = "batches"
    
    # Primary Key
    batch_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Status and Progress
    status = Column(SQLEnum(BatchStatus), default=BatchStatus.QUEUED, nullable=False)
    total_files = Column(Integer, default=0, nullable=False)
    processed_files = Column(Integer, default=0, nullable=False)
    failed_files = Column(Integer, default=0, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # User reference (simplified - in production, add proper user model)
    user_id = Column(String(255), nullable=True)
    
    # Description/Notes
    description = Column(String(500), nullable=True)
    
    # Relationships
    candidates = relationship("Candidate", back_populates="batch", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Batch {self.batch_id} - {self.status}>"
    
    @property
    def progress_percentage(self) -> float:
        """Calculate processing progress as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100
