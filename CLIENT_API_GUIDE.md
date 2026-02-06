# CV Extraction API - Integration Guide

## Overview
This API allows you to upload a CV (Resume) in PDF or Image format and instantly receive the extracted data in JSON format. This processing happens in real-time and does not require job descriptions or account logins.

## Base URL
**[Your VPS URL]**  
*Example: `http://203.0.113.45:8000` or `https://api.yourdomain.com`*

---

## Endpoint: Extract CV Data (Single or Multiple)
**URL:** `/api/extract-cv`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`

### Request Parameters

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `files` | File[] | Yes | One or more CV documents. Supports `.pdf`, `.jpg`, `.png`, `.jpeg`. |

### Example Usage

#### 1. Using cURL (Command Line)
```bash
# Upload multiple files by repeating the -F flag
curl -X POST "http://<YOUR_HOST_ADDRESS>:8000/api/extract-cv" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/path/to/resume1.pdf" \
  -F "files=@/path/to/resume2.jpg"
```

#### 2. Using Postman
1. Create a new request.
2. Set method to **POST**.
3. Set URL to `http://<YOUR_HOST_ADDRESS>:8000/api/extract-cv`.
4. Go to the **Body** tab.
5. Select **form-data**.
6. Set Key to `files` (select "File" from dropdown).
7. You can add multiple rows with the key `files` to upload multiple documents at once.
8. Click **Send**.

---

## Response Usage
The API returns a JSON object with a `batch_status` and a list of `results` for each file.

### Sample Success Response (JSON)
```json
{
  "batch_status": "completed",
  "total_files": 2,
  "results": [
    {
      "status": "success",
      "filename": "resume1.pdf",
      "extracted_data": {
        "name": "Ahmed Al-Mansoori",
        "current_position": "Senior Architect",
        "email": "ahmed@example.com",
        "phone": "+971500000000",
        "skills": ["Revit", "AutoCAD"]
        // ... (rest of extracted fields)
      }
    },
    {
      "status": "success",
      "filename": "resume2.jpg",
      "extracted_data": {
        "name": "Sarah Jones",
        // ...
      }
    }
  ]
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
