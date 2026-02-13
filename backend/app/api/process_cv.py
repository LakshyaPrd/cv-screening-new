"""
POST /api/process-cv endpoint.
Extracts CV data, evaluates profile, saves to MongoDB.
"""

import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

from app.config import settings
from app.mongodb import get_mongodb
from app.services.profile_evaluator import ProfileEvaluator

logger = logging.getLogger(__name__)
router = APIRouter()

evaluator = ProfileEvaluator()


@router.post("/process-cv", status_code=200)
async def process_cv(
    files: List[UploadFile] = File(..., description="CV files (PDF or Image)"),
):
    """
    Upload CVs → Extract with Gemini → Evaluate profile → Save to MongoDB → Return results.
    """
    from app.services.ocr_pipeline import OCRPipeline
    from app.services.ats_parser import ATSParser

    pipeline = OCRPipeline()
    ats_parser = ATSParser()

    # Get MongoDB
    try:
        db = get_mongodb()
        collection = db["candidates"]
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")
        raise HTTPException(status_code=503, detail="MongoDB unavailable")

    temp_dir = Path(settings.UPLOAD_DIR) / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for file in files:
        file_ext = Path(file.filename).suffix or ".pdf"
        temp_path = temp_dir / f"{uuid.uuid4()}{file_ext}"

        try:
            # Save uploaded file
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Step 1: Extract text using OCR
            raw_text = pipeline.extract_text(temp_path)

            # Step 2: Parse CV using ATS parser (rule-based + Gemini)
            extracted_data = ats_parser.parse(raw_text)

            # Step 3: Run ProfileEvaluator
            computed_metrics = evaluator.evaluate(extracted_data)

            # Step 4: Save to MongoDB
            document = {
                "filename": file.filename,
                "uploaded_at": datetime.utcnow(),
                "extracted_data": extracted_data,
                "computed_metrics": computed_metrics,
            }

            insert_result = await collection.insert_one(document)
            candidate_id = str(insert_result.inserted_id)

            logger.info(f"Processed and saved: {file.filename} → {candidate_id}")

            results.append({
                "status": "success",
                "filename": file.filename,
                "candidate_id": candidate_id,
                "extracted_data": extracted_data,
                "computed_metrics": computed_metrics,
            })

        except Exception as e:
            logger.error(f"Processing error for {file.filename}: {e}")
            results.append({
                "status": "failed",
                "filename": file.filename,
                "error": str(e),
            })

        finally:
            if temp_path.exists():
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    return {
        "batch_status": "completed",
        "total_files": len(files),
        "results": results,
    }


@router.get("/candidates", status_code=200)
async def get_candidates():
    """Get all processed candidates from MongoDB."""
    try:
        db = get_mongodb()
        collection = db["candidates"]
    except Exception as e:
        raise HTTPException(status_code=503, detail="MongoDB unavailable")

    candidates = []
    async for doc in collection.find().sort("uploaded_at", -1).limit(100):
        doc["_id"] = str(doc["_id"])
        candidates.append(doc)

    return {"total": len(candidates), "candidates": candidates}


@router.get("/candidates/{candidate_id}", status_code=200)
async def get_candidate(candidate_id: str):
    """Get a single candidate by MongoDB _id."""
    from bson import ObjectId

    try:
        db = get_mongodb()
        collection = db["candidates"]
    except Exception as e:
        raise HTTPException(status_code=503, detail="MongoDB unavailable")

    try:
        doc = await collection.find_one({"_id": ObjectId(candidate_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid candidate ID")

    if not doc:
        raise HTTPException(status_code=404, detail="Candidate not found")

    doc["_id"] = str(doc["_id"])
    return doc
