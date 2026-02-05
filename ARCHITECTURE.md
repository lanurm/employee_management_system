# Docker Architecture Diagram

## Complete System Overview

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                          CLIENT BROWSER                                   ║
║                     http://localhost:3000                                  ║
╚════════════════════════════════════╤════════════════════════════════════════╝
                                     │
                                     │ HTTP Request
                                     ▼
╔═══════════════════════════════════════════════════════════════════════════╗
║                      DOCKER HOST MACHINE                                  ║
║  ┌───────────────────────────────────────────────────────────────────┐   ║
║  │                    DOCKER NETWORK                                  │   ║
║  │              (employee-network - bridge)                           │   ║
║  │                                                                    │   ║
║  │  ┌─────────────────────────────────────────────────────────┐     │   ║
║  │  │         FRONTEND CONTAINER (frontend)                    │     │   ║
║  │  │  Port: 3000 → 3000 (mapped)                             │     │   ║
║  │  │                                                          │     │   ║
║  │  │  ┌──────────────────────────────────────────────────┐   │     │   ║
║  │  │  │  NGINX SERVER                                   │   │     │   ║
║  │  │  │  Listen: 0.0.0.0:3000                          │   │     │   ║
║  │  │  │                                                │   │     │   ║
║  │  │  │  / ──────────► index.html                      │   │     │   ║
║  │  │  │  /app.js ────► app.js                          │   │     │   ║
║  │  │  │  /styles.css ─► styles.css                     │   │     │   ║
║  │  │  │                                                │   │     │   ║
║  │  │  │  /api/* ─────┐                                 │   │     │   ║
║  │  │  │              │ Proxy                            │   │     │   ║
║  │  │  │              └──► http://app:8000/*             │   │     │   ║
║  │  │  │                                                │   │     │   ║
║  │  │  └──────────────────────────────────────────────────┘   │     │   ║
║  │  │                                                          │     │   ║
║  │  │  Files: /usr/share/nginx/html/                         │     │   ║
║  │  │    - index.html                                        │     │   ║
║  │  │    - app.js (with dynamic API URL detection)           │     │   ║
║  │  │    - styles.css                                        │     │   ║
║  │  │                                                          │     │   ║
║  │  └─────────────────────────────────────────────────────────┘     │   ║
║  │         ▲                              ▲                           │   ║
║  │         │                              │                           │   ║
║  │         │                              │                           │   ║
║  │         │ (static files)               │ (API proxy)               │   ║
║  │         │                              │                           │   ║
║  │  ┌──────┴──────────────────────────────┴─────────────────┐        │   ║
║  │  │         BROWSER JAVASCRIPT (app.js)                   │        │   ║
║  │  │                                                        │        │   ║
║  │  │  API_BASE_URL = (port === '3000')                     │        │   ║
║  │  │                  ? '/api'                              │        │   ║
║  │  │                  : 'http://localhost:8000'             │        │   ║
║  │  │                                                        │        │   ║
║  │  │  fetch(API_BASE_URL + '/employees')                   │        │   ║
║  │  │                │                                       │        │   ║
║  │  │                └──► http://localhost:3000/api/employees│       │   ║
║  │  │                     (proxied to backend)               │        │   ║
║  │  └────────────────────────────────────────────────────────┘        │   ║
║  │             │                              ▲                       │   ║
║  │             └──────────────────────────────┘                       │   ║
║  │                                                                    │   ║
║  │  ┌─────────────────────────────────────────────────────────┐     │   ║
║  │  │         BACKEND CONTAINER (app)                         │     │   ║
║  │  │  Port: 8000 → 8000 (mapped)                            │     │   ║
║  │  │  Hostname: app (in Docker network)                     │     │   ║
║  │  │                                                        │     │   ║
║  │  │  ┌──────────────────────────────────────────────────┐  │     │   ║
║  │  │  │  FASTAPI UVICORN SERVER                         │  │     │   ║
║  │  │  │  Listen: 0.0.0.0:8000                          │  │     │   ║
║  │  │  │                                                │  │     │   ║
║  │  │  │  Routes:                                       │  │     │   ║
║  │  │  │  - GET  / (health check)                       │  │     │   ║
║  │  │  │  - GET  /health                                │  │     │   ║
║  │  │  │  - POST /employees                             │  │     │   ║
║  │  │  │  - GET  /employees                             │  │     │   ║
║  │  │  │  - GET  /employees/{id}                        │  │     │   ║
║  │  │  │  - PUT  /employees/{id}                        │  │     │   ║
║  │  │  │  - DELETE /employees/{id}                      │  │     │   ║
║  │  │  │                                                │  │     │   ║
║  │  │  │  CORS Enabled:                                 │  │     │   ║
║  │  │  │  - allow_origins=["*"]                         │  │     │   ║
║  │  │  │  - allow_methods=["*"]                         │  │     │   ║
║  │  │  │  - allow_headers=["*"]                         │  │     │   ║
║  │  │  │                                                │  │     │   ║
║  │  │  └──────────────────────────────────────────────────┘  │     │   ║
║  │  │             │                                    ▲     │     │   ║
║  │  │             └────────────────────────────────────┘     │     │   ║
║  │  │                                                        │     │   ║
║  │  │  ┌──────────────────────────────────────────────────┐  │     │   ║
║  │  │  │  DATABASE OPERATIONS                            │  │     │   ║
║  │  │  │                                                │  │     │   ║
║  │  │  │  import mysql.connector                        │  │     │   ║
║  │  │  │  connect(host='db', port=3306, ...)           │  │     │   ║
║  │  │  │         ▼                                      │  │     │   ║
║  │  │  │  (connects to db container via hostname)       │  │     │   ║
║  │  │  │                                                │  │     │   ║
║  │  │  └──────────────────────────────────────────────────┘  │     │   ║
║  │  │         │                                               │     │   ║
║  │  │         │ mysql://db:3306                              │     │   ║
║  │  │         └──────────────────────────────────────────┐   │     │   ║
║  │  └─────────────────────────────────────────────────────────┘     │   ║
║  │                                                                    │   ║
║  │  ┌─────────────────────────────────────────────────────────┐     │   ║
║  │  │         DATABASE CONTAINER (db)                        │     │   ║
║  │  │  Port: 3307 → 3306 (mapped)                           │     │   ║
║  │  │  Hostname: db (in Docker network)                     │     │   ║
║  │  │                                                        │     │   ║
║  │  │  ┌──────────────────────────────────────────────────┐  │     │   ║
║  │  │  │  MYSQL SERVER 8.0                               │  │     │   ║
║  │  │  │  Listen: 0.0.0.0:3306                          │  │     │   ║
║  │  │  │                                                │  │     │   ║
║  │  │  │  Database: employee_db                        │  │     │   ║
║  │  │  │  Table: employees                             │  │     │   ║
║  │  │  │  ┌────────────────────────────────────────┐   │  │     │   ║
║  │  │  │  │ id  │ name  │ email  │ dept  │ salary  │   │  │     │   ║
║  │  │  │  ├─────┼───────┼────────┼───────┼─────────┤   │  │     │   ║
║  │  │  │  │  1  │ John  │ john@  │ Eng   │  75000  │   │  │     │   ║
║  │  │  │  │  2  │ Jane  │ jane@  │ Mkting│  65000  │   │  │     │   ║
║  │  │  │  └────────────────────────────────────────┘   │  │     │   ║
║  │  │  │                                                │  │     │   ║
║  │  │  │  Credentials:                                 │  │     │   ║
║  │  │  │  - User: root                                 │  │     │   ║
║  │  │  │  - Password: mrunal                           │  │     │   ║
║  │  │  │  - Password set via ENV in docker-compose     │  │     │   ║
║  │  │  │                                                │  │     │   ║
║  │  │  │  Volumes:                                      │  │     │   ║
║  │  │  │  - mysql_data (persistent storage)            │  │     │   ║
║  │  │  │                                                │  │     │   ║
║  │  │  └──────────────────────────────────────────────────┘  │     │   ║
║  │  │                                                        │     │   ║
║  │  └─────────────────────────────────────────────────────────┘     │   ║
║  │                                                                    │   ║
║  │  ENVIRONMENT VARIABLES:                                           │   ║
║  │  ┌──────────────────────────────────────────────────────────────┐│   ║
║  │  │ (Set in docker-compose.yml → app.environment)               ││   ║
║  │  │                                                              ││   ║
║  │  │ DB_HOST=db              (Docker service name)               ││   ║
║  │  │ DB_PORT=3306            (internal Docker port)              ││   ║
║  │  │ DB_USER=root                                                ││   ║
║  │  │ DB_PASSWORD=mrunal                                          ││   ║
║  │  │ DB_NAME=employee_db                                         ││   ║
║  │  │                                                              ││   ║
║  │  │ Read by: db.py                                              ││   ║
║  │  │ DB_CONFIG = {                                               ││   ║
║  │  │     "host": os.getenv("DB_HOST", "localhost"),              ││   ║
║  │  │     "port": int(os.getenv("DB_PORT", "3306")),              ││   ║
║  │  │     ...                                                      ││   ║
║  │  │ }                                                            ││   ║
║  │  └──────────────────────────────────────────────────────────────┘│   ║
║  │                                                                    │   ║
║  │  VOLUMES:                                                         │   ║
║  │  ┌──────────────────────────────────────────────────────────────┐│   ║
║  │  │ mysql_data (named volume)                                    ││   ║
║  │  │   └─ Mounted to: /var/lib/mysql (in db container)            ││   ║
║  │  │   └─ Persists database data across container restarts        ││   ║
║  │  └──────────────────────────────────────────────────────────────┘│   ║
║  │                                                                    │   ║
║  └───────────────────────────────────────────────────────────────────┘   ║
║                                                                           ║
║  COMMAND TO START ALL SERVICES:                                          ║
║  ┌───────────────────────────────────────────────────────────────────┐   ║
║  │ docker-compose up --build                                         │   ║
║  │                                                                   │   ║
║  │ This will:                                                        │   ║
║  │ 1. Build frontend image (Nginx)                                  │   ║
║  │ 2. Build backend image (FastAPI)                                 │   ║
║  │ 3. Pull database image (MySQL)                                   │   ║
║  │ 4. Create employee-network                                       │   ║
║  │ 5. Create mysql_data volume                                      │   ║
║  │ 6. Start all 3 containers with proper startup order              │   ║
║  │ 7. Connect all containers to the same network                    │   ║
║  │ 8. Run health checks on all services                             │   ║
║  └───────────────────────────────────────────────────────────────────┘   ║
║                                                                           ║
║  ACCESS POINTS:                                                          ║
║  ┌───────────────────────────────────────────────────────────────────┐   ║
║  │ Frontend:        http://localhost:3000                            │   ║
║  │ API (via Nginx): http://localhost:3000/api/*                    │   ║
║  │ API Docs:        http://localhost:3000/api/docs                 │   ║
║  │ Backend Direct:  http://localhost:8000                          │   ║
║  │ Backend Docs:    http://localhost:8000/docs                     │   ║
║  │ Database:        localhost:3307 (external port)                 │   ║
║  │                  db:3306 (internal Docker hostname)              │   ║
║  └───────────────────────────────────────────────────────────────────┘   ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

## Request Flow - Example: Get All Employees

```
USER CLICKS "REFRESH" BUTTON
         │
         ▼
   Browser (app.js)
   loadEmployees()
         │
         ▼
   Detect API_BASE_URL
   port === 3000? YES
   use '/api'
         │
         ▼
   fetch('/api/employees')
         │
         ▼ HTTP GET
   Nginx Container (localhost:3000)
   ┌─ Parse URL path /api/employees
   │
   └─ Match location /api/ rule
      └─ proxy_pass http://app:8000/
         │
         ▼ (Docker internal network)
   Backend FastAPI Container (app:8000)
   ┌─ Receive request: GET /employees
   │
   ├─ Run handler: @app.get("/employees")
   │
   ├─ Execute crud.get_employees()
   │
   └─ Connect to Database
      └─ mysql.connector.connect(host='db', port=3306)
         │
         ▼
      MySQL Container (db:3306)
      └─ Execute: SELECT * FROM employees
         │
         ▼
      Return [Employee1, Employee2, ...]
         │
         ▼
      Backend Formats Response
      Response: [
        {"id": 1, "name": "John", ...},
        {"id": 2, "name": "Jane", ...}
      ]
         │
         ▼ JSON
      Nginx Forwards Response
         │
         ▼
      Browser Receives Response
      app.js Updates DOM
      Display Table with Employees
         │
         ▼
      User Sees Updated Employee List
```

## Port Mapping Summary

```
┌─────────────────────────────────────────────────────────┐
│            HOST MACHINE (Your Computer)                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  localhost:3000  ═══════════════════════►  frontend:3000│
│                                            (Nginx)       │
│                                                          │
│  localhost:8000  ═══════════════════════►  app:8000     │
│                                            (FastAPI)     │
│                                                          │
│  localhost:3307  ═══════════════════════►  db:3306      │
│                                            (MySQL)       │
│                                                          │
└─────────────────────────────────────────────────────────┘

INSIDE DOCKER NETWORK (employee-network):
┌──────────────────────────────────────────────────────────┐
│                                                           │
│  frontend:3000  ──(request)──►  app:8000  ──(query)──►  db:3306
│  (Nginx)                        (FastAPI)                (MySQL)
│                                                           │
│  Internal names: frontend, app, db                        │
│  Internal ports: 3000, 8000, 3306                         │
│                                                           │
└──────────────────────────────────────────────────────────┘

KEY DIFFERENCE:
- External: localhost:3307 (host machine port)
- Internal: db:3306 (Docker service name and port)
```

## Data Flow Summary

```
CLIENT SIDE (Browser):
  index.html ◄── Served by Nginx
    ▲
    │ Loads
    ▼
  app.js ◄── Served by Nginx
    │ Detects: port === 3000
    │ Sets: API_BASE_URL = '/api'
    │
    ├─ fetch('/api/health') ──► Nginx ──► Backend
    │
    ├─ fetch('/api/employees') ──► Nginx ──► Backend
    │
    ├─ fetch('/api/employees', {method: 'POST'}) ──► Nginx ──► Backend
    │
    └─ fetch('/api/employees/1', {method: 'PUT'}) ──► Nginx ──► Backend

BACKEND (FastAPI):
  Receives request from Nginx
    │
    ├─ CORS Middleware (allows all origins)
    │
    ├─ Route Handler (matches endpoint)
    │
    ├─ Database Operation (connects to MySQL)
    │
    └─ Return Response (JSON)

DATABASE (MySQL):
  Receives query from Backend
    │
    ├─ Authenticate (user: root, password: mrunal)
    │
    ├─ Execute SQL (SELECT, INSERT, UPDATE, DELETE)
    │
    └─ Return Results
```

## Health Check Flow

```
docker-compose
    │
    ├─► Frontend Health Check
    │   └─ wget http://localhost:3000/health
    │      └─ Returns: 200 OK
    │      └─ Status: healthy
    │
    ├─► Backend Health Check
    │   └─ python -c "urllib.request.urlopen('http://localhost:8000/health')"
    │      └─ Returns: {"status": "healthy", ...}
    │      └─ Status: healthy
    │
    └─► Database Health Check
        └─ mysqladmin ping -h localhost -u root -pmrunal
           └─ Returns: mysqld is alive
           └─ Status: healthy

All containers healthy ═════► Application Ready
```
