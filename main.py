"""
main.py - FastAPI Application Entry Point

This is the main application file that creates the FastAPI app and defines
all REST API endpoints for the Employee Management System. It exposes
CRUD operations via HTTP methods and includes proper error handling.

Run this application using: uvicorn main:app --reload
Access API documentation at: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

# Import local modules
from models import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from db import init_database, test_connection
import crud


# Create FastAPI application instance
app = FastAPI(
    title="Employee Management System",
    description="A simple REST API for managing employee records using FastAPI and MySQL",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI documentation
    redoc_url="/redoc"     # ReDoc documentation
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Startup event - Initialize database when app starts
@app.on_event("startup")
async def startup_event():
    """
    Initialize the database and tables when the application starts.
    This ensures the required database structure exists before handling requests.
    """
    try:
        print("INFO: Starting Employee Management System...")
        init_database()
        print("INFO: Database initialization complete")
    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}")
        print("WARNING: Application may not work correctly without database")


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - Health check for the API.
    
    Returns:
        dict: Welcome message and API status
    """
    return {
        "message": "Welcome to Employee Management System API",
        "status": "running",
        "documentation": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API and database connectivity.
    
    Returns:
        dict: Health status of the application
    """
    try:
        db_status = test_connection()
        return {
            "status": "healthy" if db_status else "degraded",
            "api": "running",
            "database": "connected" if db_status else "disconnected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "api": "running",
            "database": "error",
            "debug_info": str(e)
        }


# ============== CRUD API ENDPOINTS ==============

# CREATE - POST /employees
@app.post("/employees", response_model=EmployeeResponse, status_code=201, tags=["Employees"])
async def create_employee(employee: EmployeeCreate):
    """
    Create a new employee record.
    
    This endpoint accepts employee data and creates a new record in the database.
    
    Args:
        employee: EmployeeCreate object with name, email, department, and salary
        
    Returns:
        EmployeeResponse: The created employee with generated ID
        
    Raises:
        HTTPException: 400 if email already exists, 500 for other errors
    """
    try:
        # Call CRUD function to create employee
        result = crud.create_employee(employee)
        
        if result:
            print(f"DEBUG: API - Created employee: {result}")
            return result
        else:
            raise HTTPException(status_code=500, detail="Failed to create employee")
            
    except Exception as e:
        error_message = str(e)
        print(f"ERROR: API - Create employee failed: {error_message}")
        
        # Check for duplicate email error
        if "Email already exists" in error_message:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        raise HTTPException(status_code=500, detail=f"Internal server error: {error_message}")


# READ - GET /employees (all employees)
@app.get("/employees", response_model=List[EmployeeResponse], tags=["Employees"])
async def get_all_employees(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return")
):
    """
    Retrieve all employees with pagination.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (1-1000)
        
    Returns:
        List[EmployeeResponse]: List of employee records
    """
    try:
        employees = crud.get_all_employees(skip=skip, limit=limit)
        print(f"DEBUG: API - Retrieved {len(employees)} employees")
        return employees
        
    except Exception as e:
        print(f"ERROR: API - Get all employees failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve employees: {e}")


# READ - GET /employees/{id} (single employee)
@app.get("/employees/{employee_id}", response_model=EmployeeResponse, tags=["Employees"])
async def get_employee(employee_id: int):
    """
    Retrieve a single employee by ID.
    
    Args:
        employee_id: The unique identifier of the employee
        
    Returns:
        EmployeeResponse: The employee data
        
    Raises:
        HTTPException: 404 if employee not found
    """
    try:
        employee = crud.get_employee(employee_id)
        
        if employee:
            print(f"DEBUG: API - Found employee with ID: {employee_id}")
            return employee
        else:
            print(f"DEBUG: API - Employee with ID {employee_id} not found")
            raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
            
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"ERROR: API - Get employee failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve employee: {e}")


# UPDATE - PUT /employees/{id}
@app.put("/employees/{employee_id}", response_model=EmployeeResponse, tags=["Employees"])
async def update_employee(employee_id: int, employee: EmployeeUpdate):
    """
    Update an existing employee's information.
    
    This endpoint supports partial updates - only fields provided will be updated.
    
    Args:
        employee_id: The ID of the employee to update
        employee: EmployeeUpdate object with fields to update
        
    Returns:
        EmployeeResponse: The updated employee data
        
    Raises:
        HTTPException: 404 if employee not found, 400 if email conflict
    """
    try:
        result = crud.update_employee(employee_id, employee)
        
        if result:
            print(f"DEBUG: API - Updated employee with ID: {employee_id}")
            return result
        else:
            print(f"DEBUG: API - Employee with ID {employee_id} not found for update")
            raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
            
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        print(f"ERROR: API - Update employee failed: {error_message}")
        
        if "Email already exists" in error_message:
            raise HTTPException(status_code=400, detail="Email already exists")
            
        raise HTTPException(status_code=500, detail=f"Failed to update employee: {error_message}")


# DELETE - DELETE /employees/{id}
@app.delete("/employees/{employee_id}", tags=["Employees"])
async def delete_employee(employee_id: int):
    """
    Delete an employee from the database.
    
    Args:
        employee_id: The ID of the employee to delete
        
    Returns:
        dict: Confirmation message
        
    Raises:
        HTTPException: 404 if employee not found
    """
    try:
        result = crud.delete_employee(employee_id)
        
        if result:
            print(f"DEBUG: API - Deleted employee with ID: {employee_id}")
            return {"message": f"Employee with ID {employee_id} deleted successfully"}
        else:
            print(f"DEBUG: API - Employee with ID {employee_id} not found for deletion")
            raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: API - Delete employee failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete employee: {e}")


# SEARCH - GET /employees/search/department
@app.get("/employees/search/department/{department}", response_model=List[EmployeeResponse], tags=["Employees"])
async def search_by_department(department: str):
    """
    Search for employees in a specific department.
    
    Args:
        department: The department name to search for (supports partial matching)
        
    Returns:
        List[EmployeeResponse]: List of matching employees
    """
    try:
        employees = crud.search_employees_by_department(department)
        print(f"DEBUG: API - Found {len(employees)} employees in department '{department}'")
        return employees
        
    except Exception as e:
        print(f"ERROR: API - Search by department failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search employees: {e}")


# Error handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for any unhandled exceptions.
    
    This provides a consistent error response format and logs errors for debugging.
    """
    print(f"ERROR: Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "debug_info": str(exc)
        }
    )


# Run the application (if executed directly)
if __name__ == "__main__":
    print("Starting Employee Management System API...")
    print("Access documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
