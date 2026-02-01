# Backend API Testing Guide

This guide is for the client/testers to verify the functionality of the CV Screening Backend APIs.

## 1. Accessing the Environment

- **Base URL**: `http://YOUR_VPS_IP:8004`
- **Interactive Documentation (Swagger UI)**: `http://YOUR_VPS_IP:8004/api/docs`
- **Alternative Documentation (ReDoc)**: `http://YOUR_VPS_IP:8004/api/redoc`

**Note:** Replace `YOUR_VPS_IP` with the actual IP address of the server.

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

### Step 4: View Extracted Candidates
See the data extracted from the CVs.
- **Endpoint**: `GET /api/batches/{batch_id}/candidates`
- **Parameters**: `batch_id` (from Step 2)
- **Expected Response**: A list of candidate profiles with names, emails, skills, etc.

### Step 5: Admin Metrics (Optional)
View system-wide statistics.
- **Endpoint**: `GET /api/admin/system-health`
- **Expected Response**:
  ```json
  {
    "status": "healthy",
    "metrics": {
      "total_batches": 5,
      "total_candidates": 12,
      ...
    }
  }
  ```

---

## 3. Important Notes for Testing
- **Valid Files**: The system accepts PDF, JPG, PNG, DOCX.
- **Processing Time**: OCR can take 5-10 seconds per page. Please be patient during the "processing" state.
- **CORS**: The API is currently configured to allow requests from any origin (`*`) for ease of testing.
