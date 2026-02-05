# Docker Deployment Guide

## Overview

This document explains how the frontend and backend are now properly bound together using Docker Compose.

## Problems Solved

### ❌ Before (Issues)

1. **Frontend Not Dockerized**: Only backend had a Dockerfile
2. **No Port Binding for Frontend**: Frontend files were just HTML/JS, not served by any container
3. **Hardcoded API URLs**: Frontend used `http://localhost:8000` which breaks in Docker
4. **Missing Frontend Service**: docker-compose.yml only had backend + database
5. **No Network Communication**: Frontend and backend couldn't communicate within Docker network

### ✅ After (Solution)

1. **Frontend Dockerized**: Created `frontend/Dockerfile` with Nginx
2. **Frontend Port Bound**: Frontend runs on port 3000 via Nginx
3. **Dynamic API URLs**: Frontend detects environment and uses correct API endpoint
4. **Complete Stack**: docker-compose.yml now orchestrates 3 services
5. **Internal Network**: All services communicate via `employee-network`

---

## Architecture

### Local Development (Without Docker)

```
Browser (localhost:8000)
    ↓
FastAPI Backend
    ↓
MySQL Database
```

### Docker Deployment

```
Browser (localhost:3000)
    ↓
Nginx Container (frontend:3000)
    ├─ Serves: index.html, app.js, styles.css
    ├─ Proxies: /api/* → http://app:8000/
    └─ Network: employee-network
        ↓
FastAPI Container (app:8000)
    ├─ REST API Endpoints
    └─ Network: employee-network
        ↓
MySQL Container (db:3306)
    └─ Database Storage
```

---

## File Changes

### New Files Created

#### 1. `frontend/Dockerfile`
- Uses Nginx Alpine as base image
- Serves frontend static files
- Listens on port 3000
- Includes health checks

#### 2. `frontend/nginx.conf`
- Configures Nginx server
- Routes `/api/*` to backend container
- Handles SPA client-side routing
- Caches static assets
- Implements gzip compression

### Modified Files

#### 1. `docker-compose.yml`
**Added frontend service:**
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  ports:
    - "3000:3000"
  depends_on:
    - app
```

#### 2. `frontend/app.js`
**Updated API URL detection:**
```javascript
const API_BASE_URL = (() => {
    if (port === '3000' || hostname === 'localhost') {
        return `${protocol}//${hostname}:${port}/api`;
    }
    return `${protocol}//${hostname}:8000`;
})();
```

This ensures:
- In Docker: Uses Nginx proxy at `/api`
- Local development: Uses direct backend at `:8000`

#### 3. `Dockerfile` (Backend)
**Removed frontend files:**
- Removed: `COPY frontend/ ./frontend/`
- Backend no longer needs to serve frontend files
- Nginx handles all frontend serving

---

## How It Works in Docker

### Step 1: Build Phase
```bash
docker-compose up --build
```

1. **Frontend Build**:
   - Copies index.html, app.js, styles.css to container
   - Sets up Nginx with custom configuration
   - Ready to serve on port 3000

2. **Backend Build**:
   - Installs Python dependencies
   - Copies Python application files
   - Ready to run API on port 8000

3. **Database Build**:
   - Pulls official MySQL image
   - Sets up credentials and database
   - Ready to store data

### Step 2: Service Startup
```
docker-compose up
```

1. Database starts first (mysql:8000)
2. Backend waits for database (depends_on with healthcheck)
3. Frontend waits for backend
4. All services connect via `employee-network`

### Step 3: Request Flow

**User Access Frontend:**
```
Browser → http://localhost:3000
    ↓
Nginx Container
    - Serves index.html (first request)
    - Serves app.js, styles.css (subsequent requests)
    - App.js executes in browser
```

**Frontend Makes API Request:**
```
Browser (app.js) → fetch('/api/employees')
    ↓
Nginx Container (processes /api/*)
    ↓
Proxy to http://app:8000/employees
    ↓
FastAPI Container
    - Processes request
    - Returns JSON
    ↓
Response back through Nginx
    ↓
Browser (app.js processes response)
```

### Step 4: Database Communication

**Backend Accesses Database:**
```
FastAPI Container (localhost:3306 won't work!)
    ↓
Uses Docker hostname: db:3306
    ↓
MySQL Container
    - Authenticates with credentials
    - Returns data
```

This is why `docker-compose.yml` sets:
```yaml
environment:
  - DB_HOST=db  # Docker hostname, not localhost!
```

---

## Network Configuration

### Docker Network: `employee-network`

All services connect to a custom bridge network:

```yaml
networks:
  employee-network:
    driver: bridge
```

**Benefits:**
- Services discover each other by hostname
- Isolated from other Docker networks
- Automatic DNS resolution
- Port mapping works as expected

**Service Hostnames (inside Docker):**
- `frontend:3000` - Available only from outside (via port mapping)
- `app:8000` - Available to other containers
- `db:3306` - Available to app container

**Port Mapping (outside Docker):**
- `localhost:3000` → frontend:3000
- `localhost:8000` → app:8000
- `localhost:3307` → db:3306 (note: external port is 3307 to avoid conflicts)

---

## Configuration Files Explained

### docker-compose.yml Service: Frontend

```yaml
frontend:
  build:
    context: ./frontend      # Build from frontend directory
    dockerfile: Dockerfile
  container_name: employee-management-frontend
  ports:
    - "3000:3000"           # Map port 3000 on host to 3000 in container
  depends_on:
    - app                   # Wait for backend to be ready
  restart: unless-stopped
  networks:
    - employee-network      # Connect to shared network
  healthcheck:
    test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### nginx.conf Key Sections

```nginx
# Serve static files on port 3000
server {
    listen 3000;
    root /usr/share/nginx/html;
    index index.html;
}

# Proxy API requests to backend
location /api/ {
    proxy_pass http://app:8000/;  # Route to backend container
}

# SPA routing - all requests go to index.html for client-side routing
location / {
    try_files $uri $uri/ /index.html;
}
```

### app.js API URL Detection

```javascript
// Detects if running in Docker
if (port === '3000' || hostname === 'localhost') {
    // Use Nginx proxy
    return `${protocol}//${hostname}:${port}/api`;
}
// Fallback for other environments
return `${protocol}//${hostname}:8000`;
```

---

## Deployment Steps

### 1. Verify Files Are in Place

```bash
# Should see:
# - Dockerfile (backend)
# - docker-compose.yml
# - frontend/Dockerfile
# - frontend/nginx.conf
# - frontend/app.js (updated)
# - requirements.txt
# - main.py, db.py, crud.py, models.py
```

### 2. Build Images

```bash
cd "c:\Users\Mrunal.Gund\Documents\Python project\Employee management system"
docker-compose build
```

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Verify Services

```bash
# Check running containers
docker-compose ps

# Test frontend
curl http://localhost:3000

# Test backend API
curl http://localhost:3000/api/health
curl http://localhost:8000/health

# View logs
docker-compose logs -f frontend
docker-compose logs -f app
docker-compose logs -f db
```

### 5. Access Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:3000/api/docs
- **Direct Backend**: http://localhost:8000/docs (if needed)

---

## Troubleshooting

### Frontend shows "Disconnected"

**Cause**: Frontend can't reach backend API

**Solution**:
```bash
# Check if backend is running
docker-compose ps

# Check backend logs
docker-compose logs app

# Test API directly
curl http://localhost:3000/api/health
```

### "Cannot GET /" on frontend

**Cause**: Nginx not serving files correctly

**Solution**:
```bash
# Check nginx config
docker exec employee-management-frontend cat /etc/nginx/nginx.conf

# Check if files are in container
docker exec employee-management-frontend ls -la /usr/share/nginx/html/

# Rebuild frontend
docker-compose up --build frontend
```

### Database connection error in backend

**Cause**: Backend can't find database

**Solution**:
```bash
# Check DB is running
docker-compose ps

# Check DB logs
docker-compose logs db

# Verify DB_HOST is "db" (not localhost)
docker-compose logs app | grep DB_HOST
```

### Port already in use

**Cause**: Another service using ports 3000, 8000, or 3307

**Solution**:
```bash
# Find what's using the port
netstat -ano | findstr :3000

# Either stop that process or change ports in docker-compose.yml:
# ports:
#   - "3001:3000"  # Use 3001 instead
```

### Container keeps restarting

**Cause**: Application crashes on startup

**Solution**:
```bash
# Check logs
docker-compose logs app --tail=50

# Rebuild and restart
docker-compose down -v
docker-compose up --build
```

---

## Environment Variables

### Backend (FastAPI in Docker)

Set in `docker-compose.yml` under `app.environment`:

```yaml
environment:
  - DB_HOST=db              # Docker hostname
  - DB_PORT=3306            # Internal Docker port
  - DB_USER=root
  - DB_PASSWORD=mrunal
  - DB_NAME=employee_db
```

Backend code (`db.py`) should read these:

```python
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "employee_db"),
    "port": int(os.getenv("DB_PORT", 3306))
}
```

### Frontend (JavaScript in Docker)

App.js automatically detects:
- Running on port 3000 → Use `/api` proxy
- Running on port 8000 → Use direct connection

---

## Cleanup

### Stop Services

```bash
docker-compose down
```

### Remove Data Volumes (Reset Database)

```bash
docker-compose down -v
```

### Remove Images

```bash
docker-compose down --rmi all
```

---

## Production Considerations

### Current Setup (Development)

- CORS allows all origins: `allow_origins=["*"]`
- No authentication/authorization
- Database password hardcoded

### For Production

1. **Security**:
   - Change database password
   - Implement authentication (JWT tokens)
   - Restrict CORS origins
   - Use environment files (.env)

2. **Performance**:
   - Enable Redis caching
   - Use connection pooling
   - Implement rate limiting
   - Use CDN for static files

3. **Monitoring**:
   - Add logging (ELK stack)
   - Monitor container health
   - Set up alerts
   - Use health checks

4. **Scalability**:
   - Use Docker Swarm or Kubernetes
   - Implement load balancing
   - Scale backend horizontally
   - Use managed database service

---

## Summary

The application is now properly containerized with:

✅ Frontend served on port 3000 via Nginx  
✅ Backend API on port 8000 via FastAPI  
✅ Database on port 3307 (3306 internal) via MySQL  
✅ All services connected via Docker network  
✅ Frontend and backend properly bound together  
✅ API proxy through Nginx for seamless communication  
✅ Health checks for all services  
✅ Proper startup order and dependencies  

The entire stack can be deployed with a single command:

```bash
docker-compose up --build
```

Access the application at: **http://localhost:3000**
