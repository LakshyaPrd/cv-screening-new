# Deployment Guide for Backend API Testing

To allow your client to test **only the Backend APIs**, follow these streamlined instructions.

## 1. Prepare for Deployment

I have already configured `docker-compose.yml` with non-conflicting ports:
- **Backend API**: Port `8004` (Access at `http://YOUR_VPS_IP:8004/api/docs`)
- **Database**: Port `5433`
- **Redis**: Port `6380`

## 2. Transfer Code to VPS

1. **Copy your project** to the VPS (using Git or SCP).
   ```bash
   scp -r "c:\Lakshya\cv-screening-new" root@your_vps_ip:/root/
   ```
   *(Or git clone if you are using a repo)*

## 3. Configure for API Testing

1. **SSH into your VPS** and go to the folder:
   ```bash
   cd cv-screening-new
   ```

2. **Edit `docker-compose.yml` to allow easy access**:
   We will set CORS to `*` so your client can test from anywhere (Postman, etc.) without issues.
   
   ```bash
   nano docker-compose.yml
   ```
   
   Find the backend environment section and change `CORS_ORIGINS`:
   ```yaml
   - CORS_ORIGINS=*
   ```
   *(This is easier than finding the exact client IP)*

   *Press `Ctrl+X`, `Y`, `Enter` to save.*

## 4. Launch STRICTLY the Backend

Since you only want to test the APIs, simply run the backend services. This saves resources by NOT starting the frontend.

```bash
docker compose up -d --build backend postgres redis celery_worker
```

## 5. Share with Client

Give your client the following details:

- **API Documentation (Swagger UI)**: 
  `http://YOUR_VPS_IP:8004/api/docs`
  *(They can try out endpoints directly here)*

- **Base API URL**: 
  `http://YOUR_VPS_IP:8004`

- **Health Check**: 
  `http://YOUR_VPS_IP:8004/health`

## Troubleshooting

- **Check Logs**:
  ```bash
  docker compose logs -f backend
  ```
- **Restart**:
  ```bash
  docker compose restart backend
  ```
