# Deployment Guide (Git Workflow)

## 1. Local Steps (Your Machine)

1. **Commit your changes**:
   Make sure the updated `docker-compose.yml` (with new ports) is committed.
   ```bash
   git add .
   git commit -m "Configure production ports and deployment settings"
   ```

2. **Push to GitHub**:
   ```bash
   git push origin main
   ```
   *(Or whatever branch you are using)*

## 2. Server Steps (VPS)

1. **SSH into your VPS**:
   ```bash
   ssh root@your_vps_ip
   ```

2. **Clone/Pull the Code**:
   If this is the **first time**:
   ```bash
   git clone https://github.com/LakshyaPrd/cv-screening-new.git
   cd cv-screening-new
   ```
   
   If you **already cloned it**:
   ```bash
   cd cv-screening-new
   git pull origin main
   ```

3. **Configure the Environment**:
   **Crucial Step**: You must edit `docker-compose.yml` on the server to set the API URL correctly if you haven't done so in the code itself.
   
   However, since we are doing **Backend API Testing Only**, we just need to ensure CORS allows external access.
   
   Edit the file:
   ```bash
   nano docker-compose.yml
   ```
   
   Ensure this line exists in the `backend` service:
   `CORS_ORIGINS=*`
   
   *(If you pushed the file with CORS_ORIGINS=*, you can skip this editing step).*

4. **Deploy Backend Only**:
   Run this command to start only the necessary services for API testing (Backend + Database + Redis):
   
   ```bash
   docker compose up -d --build backend postgres redis celery_worker
   ```
   
   *This saves memory by ignoring the frontend container.*

## 3. Verify Deployment

Run:
```bash
docker ps
```
You should see 4 containers running (backend, db, redis, celery).

## 4. What to Send to the Client

**Files to Share:**
- Send them the `API_TESTING_GUIDE.md` file (I have created this in your project root).

**Information to Share:**
- **Their VPS IP Address**: Remind them to replace `YOUR_VPS_IP` in the guide with their actual IP.
- **Access URL**: `http://<VPS_IP>:8004/api/docs`
