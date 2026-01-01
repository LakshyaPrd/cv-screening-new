from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class BatchStatus(str, Enum):
    """Batch processing status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchCreate(BaseModel):
    """Schema for creating a new batch."""
    description: Optional[str] = Field(None, max_length=500)
    user_id: Optional[str] = Field(None, max_length=255)


class BatchResponse(BaseModel):
    """Schema for batch response."""
    batch_id: UUID
    status: BatchStatus
    total_files: int
    processed_files: int
    failed_files: int
    progress_percentage: float
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class BatchDetailResponse(BatchResponse):
    """Extended batch response with candidates."""
    user_id: Optional[str]


class BatchListResponse(BaseModel):
    """Schema for list of batches."""
    batches: List[BatchResponse]
    total: int
