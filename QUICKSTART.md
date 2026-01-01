# CV Screening Platform - Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Tesseract OCR
- Poppler utilities

## Option 1: Docker (Recommended)

The easiest way to run the entire platform:

```bash
# Clone or navigate to project directory
cd cv-screening-new

# Start all services
docker-compose up

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

## Option 2: Manual Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env
# Edit .env with your settings

# Run the backend
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run the frontend
npm run dev
```

### Database Setup

```bash
# Create PostgreSQL database
createdb cv_screening

# The application will automatically create tables on first run
```

## Usage

### 1. Upload CVs

- Navigate to `http://localhost:3000/upload`
- Drag and drop multiple PDF/image files
- Click "Upload Batch"
- Note the batch ID returned

### 2. Create Job Description

- Navigate to `http://localhost:3000/job-descriptions/create`
- Fill in job title, description, required skills, and tools
- Adjust scoring weights if needed
- Submit

### 3. Match Candidates

- Navigate to job description details page
- Click "Match Candidates"
- View ranked candidates with scores
- Filter by minimum score, skills, tools, etc.

### 4. Review Results

- Each candidate shows:
  - Total score (0-100)
  - Score breakdown by category
  - Explainable justification
  - Contact information
- Shortlist or reject candidates

## API Documentation

Interactive API docs available at: `http://localhost:8000/api/docs`

Key endpoints:
- `POST /api/upload/batch` - Upload CV batch
- `POST /api/jd` - Create job description
- `POST /api/jd/{jd_id}/match` - Match candidates
- `GET /api/jd/{jd_id}/matches` - Get ranked results

## Admin Panel

Access admin features at `http://localhost:3000/admin`:
- Manage skills dictionary
- Configure scoring weights
- Monitor system health
- View batch processing status

## Troubleshooting

### Tesseract not found

**Windows:**
```bash
# Install via Chocolatey
choco install tesseract

# Or download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Poppler not found

**Windows:**
```bash
choco install poppler
```

**macOS:**
```bash
brew install poppler
```

**Linux:**
```bash
sudo apt-get install poppler-utils
```

### Database connection errors

1. Ensure PostgreSQL is running
2. Check `.env` file has correct `DATABASE_URL`
3. Verify database exists: `psql -l`

### Redis connection errors

1. Ensure Redis is running: `redis-cli ping`
2. Check `REDIS_URL` in `.env`

## Production Deployment

See `docs/deployment.md` for AWS deployment guide.

## Support

For issues or questions, contact your development team.
