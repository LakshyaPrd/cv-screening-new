# CV Screening Platform

A scalable CV & Portfolio OCR, Job Description Matching & CRM integration platform.

## Tech Stack

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL + Redis
- **OCR**: Tesseract (open-source)
- **Queue**: Celery + Redis

## Features

- ✅ Bulk CV & Portfolio upload (100s-1000s per batch)
- ✅ Open-source OCR (Tesseract) - NO recurring costs
- ✅ Rule-based JD matching - NO AI/ML
- ✅ Explainable candidate scoring
- ✅ CRM integration
- ✅ Scalable architecture (millions of users)

## Project Structure

```
cv-screening-new/
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
└── docker-compose.yml
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Tesseract OCR

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Setup

```bash
docker-compose up
```

## Documentation

- [Implementation Plan](./docs/implementation_plan.md)
- [API Documentation](http://localhost:8000/docs)

## License

Proprietary - Client Owned
