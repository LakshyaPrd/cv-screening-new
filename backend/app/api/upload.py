from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import os
import shutil
from pathlib import Path

from app.database import get_db
from app.config import settings
from app.models.batch import Batch, BatchStatus
from app.schemas.batch import BatchCreate, BatchResponse
from app.services.file_validator import FileValidator
from app.workers.ocr_tasks import process_cv_batch

router = APIRouter()


@router.post("/upload/batch", response_model=BatchResponse, status_code=201)
async def upload_batch(
    files: List[UploadFile] = File(..., description="CV and portfolio files"),
    description: str = None,
    user_id: str = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    """
    Upload a batch of CV/portfolio files for processing.
    
    - Validates file types and sizes
    - Creates batch tracking record
    - Queues OCR processing tasks
    - Returns batch ID for status tracking
    """
    # Valiate files
    validator = FileValidator()
    
    for file in files:
        # Validate file
        validation_result = await validator.validate_file(file)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file '{file.filename}': {validation_result['error']}"
            )
    
    # Create batch record
    batch = Batch(
        total_files=len(files),
        status=BatchStatus.QUEUED,
        description=description,
        user_id=user_id,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    
    # Create batch directory
    batch_dir = Path(settings.UPLOAD_DIR) / str(batch.batch_id)
    batch_dir.mkdir(parents=True, exist_ok=True)
    
    # Save files
    file_paths = []
    for idx, file in enumerate(files):
        file_path = batch_dir / f"{idx}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_paths.append(str(file_path))
    
    # Queue processing task (async via Celery)
    # For now, we'll use FastAPI background tasks
    # In production, replace with Celery
    background_tasks.add_task(
        process_cv_batch_task,
        batch_id=str(batch.batch_id),
        file_paths=file_paths,
    )
    
    return BatchResponse.from_orm(batch)



@router.post("/extract-cv", status_code=200)
async def extract_cv_data(
    files: List[UploadFile] = File(..., description="CV files (PDF or Image)"),
):
    """
    Upload multiple CVs and get the extracted data immediately (JSON).
    Does NOT save to database.
    """
    import uuid
    
    # Create temp directory if not exists
    temp_dir = Path(settings.UPLOAD_DIR) / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Import pipeline here to avoid circular dependency
    from app.services.ocr_pipeline import OCRPipeline
    pipeline = OCRPipeline()
    
    results = []
    
    for file in files:
        # Generate unique filename
        file_ext = Path(file.filename).suffix
        if not file_ext:
            file_ext = ".pdf" # Default to PDF if no extension
            
        temp_path = temp_dir / f"{uuid.uuid4()}{file_ext}"
        
        try:
            # Save uploaded file
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            # Extract text
            raw_text = pipeline.extract_text(temp_path)
            
            # Extract data
            extracted_data = pipeline.extractor.extract_comprehensive_data(raw_text)
            
            results.append({
                "status": "success",
                "filename": file.filename,
                "extracted_data": extracted_data,
            })
            
        except Exception as e:
            print(f"Extraction error for {file.filename}: {str(e)}")
            results.append({
                "status": "failed",
                "filename": file.filename,
                "error": str(e)
            })
            
        finally:
            # Cleanup
            if temp_path.exists():
                try:
                    os.remove(temp_path)
                except Exception as e:
                    print(f"Failed to delete temp file {temp_path}: {e}")
    
    return {
        "batch_status": "completed",
        "total_files": len(files),
        "results": results
    }

def process_cv_batch_task(batch_id: str, file_paths: List[str]):
    """
    Background task to process CV batch.
    This would be replaced by Celery task in production.
    """
    # Import here to avoid circular dependency
    from app.services.ocr_pipeline import OCRPipeline
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Get batch
        batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
        if not batch:
            return
        
        # Update status
        batch.status = BatchStatus.PROCESSING
        db.commit()
        
        # Process files
        pipeline = OCRPipeline()
        for file_path in file_paths:
            try:
                # Process single file
                result = pipeline.process_file(file_path, batch_id, db)
                
                # Update progress
                batch.processed_files += 1
                db.commit()
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                batch.failed_files += 1
                db.commit()
        
        # Mark batch as completed
        batch.status = BatchStatus.COMPLETED
        from datetime import datetime
        batch.completed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        # Mark batch as failed
        batch.status = BatchStatus.FAILED
        db.commit()
        print(f"Batch {batch_id} failed: {e}")
        
    finally:
        db.close()

