# CV Extraction API - Integration Guide

## Overview
This API allows you to upload a CV (Resume) in PDF or Image format and instantly receive the extracted data in JSON format. This processing happens in real-time and does not require job descriptions or account logins.

## Base URL
**[Your VPS URL]**  
*Example: `http://203.0.113.45:8000` or `https://api.yourdomain.com`*

---

## Endpoint: Extract CV Data

**URL:** `/api/extract-cv`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`

### Request Parameters

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `file` | File | Yes | The CV document. Supports `.pdf`, `.jpg`, `.png`, `.jpeg`. |

### Example Usage

#### 1. Using cURL (Command Line)
```bash
curl -X POST "http://<YOUR_HOST_ADDRESS>:8000/api/extract-cv" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/resume.pdf"
```

#### 2. Using Postman
1. Create a new request.
2. Set method to **POST**.
3. Set URL to `http://<YOUR_HOST_ADDRESS>:8000/api/extract-cv`.
4. Go to the **Body** tab.
5. Select **form-data**.
6. Set Key to `file` (make sure to select "File" from the dropdown on the right of the key input).
7. Upload your test PDF or Image in the Value column.
8. Click **Send**.

---

## Response Usage
The API returns a JSON object with a `status`, `filename`, and a detailed `extracted_data` object.

### Sample Success Response (JSON)
```json
{
  "status": "success",
  "filename": "candidate_cv.pdf",
  "extracted_data": {
    "name": "Ahmed Al-Mansoori",
    "email": "ahmed.mansoori@example.com",
    "phone": "+971501234567",
    "location": "Dubai, UAE",
    "current_position": "Senior Architect",
    "total_experience_years": 8.5,
    "gcc_experience_years": 5.0,
    "education": [
      {
        "degree": "Bachelor of Architecture",
        "year": "2015"
      }
    ],
    "skills": [
      "AutoCAD",
      "Revit",
      "SketchUp",
      "BIM 360"
    ],
    "portfolio_url": "https://behance.net/example",
    "english_proficiency": "Fluent"
  }
}
```

### Response Fields Guide

*   **`name`**: Full name if detected.
*   **`email` / `phone`**: Contact information.
*   **`current_position`**: The inferred job title from the most recent experience.
*   **`total_experience_years`**: Calculated total years based on work history dates.
*   **`gcc_experience_years`**: Specific experience within UAE, KSA, Qatar, Kuwait, Bahrain, and Oman.
*   **`skills`**: List of technical skills found.
*   **`software_experience`**: Detailed breakdown of software proficiency (e.g., Revit - Expert).
*   **`work_history`**: Array of previous jobs with titles, companies, and dates.

---

## Error Codes

*   **200 OK**: Extraction successful.
*   **422 Validation Error**: File missing or incorrect parameter name (must be `file`).
*   **500 Internal Server Error**: The file could not be processed (e.g., corrupted PDF).
