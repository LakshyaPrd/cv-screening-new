"""
Celery tasks for OCR processing.
These can be used in production instead of FastAPI BackgroundTasks.
"""
from celery import shared_task
from app.workers.celery_app import celery_app


@celery_app.task(name="process_cv_batch")
def process_cv_batch(batch_id: str, file_paths: list):
    """
    Process a batch of CV files.
    
    Args:
        batch_id: Batch UUID
        file_paths: List of file paths to process
    """
    from app.database import SessionLocal
    from app.models.batch import Batch, BatchStatus
    from app.services.ocr_pipeline import OCRPipeline
    from datetime import datetime
    
    db = SessionLocal()
    try:
        # Get batch
        batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
        if not batch:
            return {"status": "error", "message": "Batch not found"}
        
        # Update status
        batch.status = BatchStatus.PROCESSING
        db.commit()
        
        # Process files
        pipeline = OCRPipeline()
        for file_path in file_paths:
            try:
                result = pipeline.process_file(file_path, batch_id, db)
                batch.processed_files += 1
                db.commit()
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                batch.failed_files += 1
                db.commit()
        
        # Mark batch as completed
        batch.status = BatchStatus.COMPLETED
        batch.completed_at = datetime.utcnow()
        db.commit()
        
        return {
            "status": "success",
            "batch_id": batch_id,
            "processed": batch.processed_files,
            "failed": batch.failed_files,
        }
        
    except Exception as e:
        # Mark batch as failed
        if batch:
            batch.status = BatchStatus.FAILED
            db.commit()
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()
