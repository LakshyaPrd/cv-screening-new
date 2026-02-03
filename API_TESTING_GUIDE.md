# Backend API Testing Guide

This guide is for the client/testers to verify the functionality of the CV Screening Backend APIs.

## 1. Accessing the Environment

- **Base URL**: `http://76.13.17.251:8004`
- **Interactive Documentation (Swagger UI)**: `http://76.13.17.251:8004/api/docs`
- **Alternative Documentation (ReDoc)**: `http://76.13.17.251:8004/api/redoc`

---

## 2. API Testing Workflow

Follow this sequence to test the core features of the system solely through the APIs.

### Step 1: Health Check
Verify the system is running.
- **Endpoint**: `GET /health`
- **Expected Response**:
  ```json
  {
    "status": "healthy",
    "app": "CV Screening Platform",
    "version": "1.0.0"
  }
  ```

### Step 2: Upload CVs (Batch Upload) 
Upload one or more CV files (PDF/Images) to be processed.
- **Endpoint**: `POST /api/upload/batch`
- **Body**: `form-data`
  - `files`: Select multiple files from your computer.
- **Expected Response**:
  ```json
  {
    "batch_id": "uuid-string-here",
    "status": "queued",
    "total_files": 2
  }
  ```
**Action**: Copy the `batch_id` from the response. You will need it.

### Step 3: Check Processing Status
Check if your uploaded files have been processed.
- **Endpoint**: `GET /api/batches/{batch_id}`
- **Parameters**: `batch_id` (from Step 2)
- **Expected Response**:
  ```json
  {
    "batch_id": "...",
    "status": "completed",
    "processed_files": 2,
    "failed_files": 0
  }
  ```
*Wait until `"status"` is `"completed"` before proceeding.*

---

## 3. Finding the Best Match (Ranking Candidates)

Once candidates are uploaded (Step 2), you need to create a Job Description (JD) to match them against.

### Step 4: Create a Job Description
Define the role you are looking for.
- **Endpoint**: `POST /api/jd`
- **Body**:
  ```json
  {
    "title": "Senior Python Developer",
    "description": "Looking for an expert backend engineer.",
    "must_have_skills": ["Python", "FastAPI", "SQL"],
    "nice_to_have_skills": ["AWS", "Docker"],
    "required_tools": ["Git", "Jira"],
    "experience_years": 5
  }
  ```
- **Expected Response**:
  ```json
  {
    "jd_id": "uuid-for-this-job",
    "title": "Senior Python Developer",
    ...
  }
  ```
**Action**: Copy the `jd_id` from the response.

### Step 5: Run Matching Algorithm
Trigger the AI to compare all candidates against this specific JD.
- **Endpoint**: `POST /api/jd/{jd_id}/match`
- **Parameters**: `jd_id` (from Step 4)
- **Expected Response**:
  ```json
  {
    "message": "Matching process started",
    "status_url": "/api/jd/{jd_id}/matches"
  }
  ```

### Step 6: Get Ranked Results (The Best Match)
View the candidates sorted by their match score (Highest % first).
- **Endpoint**: `GET /api/jd/{jd_id}/matches`
- **Parameters**: `jd_id` (from Step 4)
- **Expected Response**: A list of candidates ordered by score.
  ```json
  {
    "matches": [
      {
        "candidate_name": "John Doe",
        "total_score": 92.5,
        "skill_score": 95,
        "matched_skills": ["Python", "SQL"]
      },
      ...
    ]
  }
  ```
The first candidate in this list is your **Best Match**.

---

## 4. Important Notes for Testing
- **Valid Files**: The system accepts PDF, JPG, PNG, DOCX.
- **Processing Time**: OCR can take 5-10 seconds per page. Please be patient during the "processing" state.
- **CORS**: The API allows requests from any origin (`*`) for ease of testing.
