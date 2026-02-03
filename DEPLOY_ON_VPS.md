# Full Deployment Guide (Frontend + Backend)

## 1. Local Steps (Your Machine)

Since you have already edited `docker-compose.yml` with the correct IP (`76.13.17.251`), simply save and push.

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Configure frontend and backend for production IP"
   ```

2. **Push to GitHub**:
   ```bash
   git push origin main
   ```

## 2. Server Steps (VPS)

1. **SSH into your VPS**:
   ```bash
   ssh root@76.13.17.251
   ```

2. **Pull the latest code**:
   ```bash
   cd cv-screening-new
   git pull origin main
   ```

3. **Deploy Everything**:
   Run this command to build and start **ALL** services (Frontend, Backend, Database, etc.):
   
   ```bash
   docker compose up -d --build
   ```
   *(This will take a few minutes to build the frontend).*

## 3. Verify Deployment

Run:
```bash
docker ps
```
You should see 5 containers running:
1. `cv_screening_frontend`
2. `cv_screening_backend`
3. `cv_screening_celery`
4. `cv_screening_db`
5. `cv_screening_redis`

## 4. Access Links

Give these links to your client:

- **Frontend Application**: `http://76.13.17.251:3006`
  *(This is the main UI)*

- **Backend API Docs**: `http://76.13.17.251:8004/api/docs`
  *(Swagger UI for testing APIs)*

## 5. Troubleshooting Frontend

If the frontend loads but cannot fetch data (e.g. "Network Error"):
1. Open the browser's Developer Tools (F12).
2. Go to the **Console** tab.
3. Check if there are errors connecting to `http://76.13.17.251:8004`.
4. Ensure `CORS_ORIGINS` in `docker-compose.yml` includes `http://76.13.17.251:3006`.
