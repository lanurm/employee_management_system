# Employee Management System

A simple REST API backend for managing employee records using **Python**, **FastAPI**, and **MySQL**.

## 📁 Project Structure

```
employee_management_system/
├── main.py           # FastAPI application with REST endpoints
├── db.py             # MySQL database connection handling
├── models.py         # Employee class and Pydantic models
├── crud.py           # CRUD operations (Create, Read, Update, Delete)
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
```

## 🗄️ Database Setup

### Prerequisites
- MySQL Server installed and running
- MySQL client access (command line or workbench)

### SQL Statements

Run these SQL commands in your MySQL client to set up the database:

```sql
-- Create the database
CREATE DATABASE IF NOT EXISTS employee_db;

-- Use the database
USE employee_db;

-- Create the employees table
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Optional: Insert sample data
INSERT INTO employees (name, email, department, salary) VALUES
('John Doe', 'john.doe@company.com', 'Engineering', 75000.00),
('Jane Smith', 'jane.smith@company.com', 'Marketing', 65000.00),
('Bob Wilson', 'bob.wilson@company.com', 'Engineering', 80000.00);
```

### Configure Database Connection

Edit `db.py` and update the connection settings:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",           # Your MySQL username
    "password": "password",   # Your MySQL password
    "database": "employee_db"
}
```

## 🚀 How to Run the Project

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd employee_management_system

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start the Server

```bash
# Run with Uvicorn (development mode with auto-reload)
uvicorn main:app --reload

# Or run directly
python main.py
```

### Step 3: Access the API

- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message and API status |
| GET | `/health` | Health check with database status |
| POST | `/employees` | Create a new employee |
| GET | `/employees` | Get all employees (with pagination) |
| GET | `/employees/{id}` | Get employee by ID |
| PUT | `/employees/{id}` | Update employee by ID |
| DELETE | `/employees/{id}` | Delete employee by ID |
| GET | `/employees/search/department/{dept}` | Search by department |

## 📝 API Usage Examples

### Create Employee (POST /employees)

**Request:**
```json
{
    "name": "John Doe",
    "email": "john.doe@company.com",
    "department": "Engineering",
    "salary": 75000.00
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@company.com",
    "department": "Engineering",
    "salary": 75000.00
}
```

### Get All Employees (GET /employees)

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@company.com",
        "department": "Engineering",
        "salary": 75000.00
    }
]
```

### Update Employee (PUT /employees/1)

**Request:**
```json
{
    "salary": 80000.00
}
```

### Delete Employee (DELETE /employees/1)

**Response (200 OK):**
```json
{
    "message": "Employee with ID 1 deleted successfully"
}
```

## 🐛 Debugging and Error Handling

This project implements comprehensive error handling using `try-except` blocks for stability and debugging.

### How Debugging Works

1. **Console Logging**: All operations print `DEBUG`, `INFO`, `WARNING`, and `ERROR` messages to the console:
   ```
   DEBUG: Created employee with ID: 1
   ERROR: Failed to connect to MySQL database
   DEBUG: Error Code: 1049
   DEBUG: Unknown database - Make sure 'employee_db' exists
   ```

2. **HTTP Error Responses**: The API returns meaningful error messages:
   - `400 Bad Request`: Invalid input (e.g., duplicate email)
   - `404 Not Found`: Resource doesn't exist
   - `500 Internal Server Error`: Database or server errors

3. **Common Errors and Solutions**:

   | Error | Cause | Solution |
   |-------|-------|----------|
   | Access denied (1045) | Wrong credentials | Check username/password in `db.py` |
   | Unknown database (1049) | Database not created | Run the SQL setup commands |
   | Can't connect (2003) | MySQL not running | Start MySQL server |
   | Duplicate entry (1062) | Email already exists | Use a unique email |

4. **Debug Flow in Code**:
   ```python
   try:
       # Attempt database operation
       result = cursor.execute(query)
   except Error as e:
       # Log error details for debugging
       print(f"ERROR: Operation failed")
       print(f"DEBUG: Error Code: {e.errno}")
       print(f"DEBUG: Error Message: {e.msg}")
       # Raise meaningful exception
       raise Exception(f"Operation failed: {e}")
   finally:
       # Always clean up resources
       cursor.close()
   ```

## 🔧 Python Concepts Used

This project demonstrates the following Python concepts:

1. **Variables and Data Types**: Strings, integers, floats, dictionaries, lists
2. **Conditionals**: `if-elif-else` for validation and flow control
3. **Loops**: `for` loops for processing results
4. **Functions**: Modular functions for each operation
5. **Classes (OOP)**: Employee class with encapsulation and methods
6. **Modules**: Organized code across multiple files
7. **Error Handling**: `try-except-finally` blocks throughout
8. **Type Hints**: Function annotations for better code documentation

## 📄 License

This project is for educational purposes only.
