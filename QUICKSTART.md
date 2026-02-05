# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Build the Application

```bash
cd "c:\Users\Mrunal.Gund\Documents\Python project\Employee management system"
docker-compose build
```

### Step 2: Start All Services

```bash
docker-compose up -d
```

### Step 3: Access the Application

Open your browser and go to: **http://localhost:3000**

---

## ✅ Verification

Check that all services are running:

```bash
docker-compose ps
```

Expected output:
```
NAME                           STATUS
employee-management-frontend   Up (healthy)
employee-management-api        Up (healthy)
employee-management-db         Up (healthy)
```

Test the API:

```bash
curl http://localhost:3000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "api": "running",
  "database": "connected"
}
```

---

## 🔧 Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f app
docker-compose logs -f db
```

### Stop Services

```bash
docker-compose down
```

### Restart Services

```bash
docker-compose restart
```

### Reset Database (Remove Volume)

```bash
docker-compose down -v
docker-compose up -d
```

---

## 📍 Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API Docs (Swagger) | http://localhost:3000/api/docs |
| API Docs (ReDoc) | http://localhost:3000/api/redoc |
| Backend Direct | http://localhost:8000 |
| Backend API Docs | http://localhost:8000/docs |

---

## 🎯 What's Fixed

✅ Frontend is now dockerized (Nginx container)  
✅ Frontend runs on port 3000  
✅ Backend runs on port 8000  
✅ Database runs on port 3307  
✅ Frontend and backend are properly connected  
✅ API requests flow through Nginx proxy  
✅ All services communicate via Docker network  

---

## 📚 More Information

- See **README.md** for full documentation
- See **DOCKER_DEPLOYMENT.md** for detailed Docker setup explanation
- See **AWS_DEPLOYMENT.md** for cloud deployment instructions
