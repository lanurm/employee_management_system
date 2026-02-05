"""
crud.py - CRUD Operations Module

This module contains all CRUD (Create, Read, Update, Delete) operations
for managing employee records in the MySQL database. Each function includes
proper error handling using try-except blocks for debugging and stability.
"""

from typing import List, Optional, Dict, Any
from mysql.connector import Error
from db import get_connection, close_connection
from models import Employee, EmployeeCreate, EmployeeUpdate


def create_employee(employee_data: EmployeeCreate) -> Optional[Dict[str, Any]]:
    """
    Create a new employee record in the database.
    
    Args:
        employee_data: EmployeeCreate object containing employee details
        
    Returns:
        dict: The created employee data with generated ID, or None if failed
        
    Raises:
        Exception: If database operation fails
    """
    connection = None
    cursor = None
    
    try:
        # Establish database connection
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # SQL INSERT query with parameterized values (prevents SQL injection)
        insert_query = """
        INSERT INTO employees (name, email, department, salary)
        VALUES (%s, %s, %s, %s)
        """
        
        # Values tuple for the query
        values = (
            employee_data.name,
            employee_data.email,
            employee_data.department,
            employee_data.salary
        )
        
        # Execute the insert query
        cursor.execute(insert_query, values)
        connection.commit()
        
        # Get the auto-generated ID
        new_id = cursor.lastrowid
        print(f"DEBUG: Created employee with ID: {new_id}")
        
        # Return the created employee data
        return {
            "id": new_id,
            "name": employee_data.name,
            "email": employee_data.email,
            "department": employee_data.department,
            "salary": employee_data.salary
        }
        
    except Error as e:
        print(f"ERROR: Failed to create employee")
        print(f"DEBUG: Error Code: {e.errno}, Message: {e.msg}")
        
        # Handle duplicate email error
        if e.errno == 1062:
            raise Exception("Email already exists in the database")
        
        raise Exception(f"Failed to create employee: {e}")
        
    finally:
        # Always clean up resources
        if cursor:
            cursor.close()
        if connection:
            close_connection(connection)


def get_employee(employee_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single employee by their ID.
    
    Args:
        employee_id: The unique identifier of the employee
        
    Returns:
        dict: Employee data if found, None if not found
    """
    connection = None
    cursor = None
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # SQL SELECT query with parameterized ID
        select_query = "SELECT id, name, email, department, salary FROM employees WHERE id = %s"
        cursor.execute(select_query, (employee_id,))
        
        # Fetch single result
        result = cursor.fetchone()
        
        if result:
            print(f"DEBUG: Found employee with ID: {employee_id}")
            # Convert Decimal to float for JSON serialization
            result['salary'] = float(result['salary'])
            return result
        else:
            print(f"DEBUG: No employee found with ID: {employee_id}")
            return None
            
    except Error as e:
        print(f"ERROR: Failed to retrieve employee")
        print(f"DEBUG: Error Code: {e.errno}, Message: {e.msg}")
        raise Exception(f"Failed to retrieve employee: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            close_connection(connection)


def get_all_employees(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Retrieve all employees with pagination support.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        list: List of employee dictionaries
    """
    connection = None
    cursor = None
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # SQL SELECT query with LIMIT and OFFSET for pagination
        select_query = "SELECT id, name, email, department, salary FROM employees LIMIT %s OFFSET %s"
        cursor.execute(select_query, (limit, skip))
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Convert Decimal to float for each result
        for result in results:
            result['salary'] = float(result['salary'])
        
        print(f"DEBUG: Retrieved {len(results)} employees")
        return results
        
    except Error as e:
        print(f"ERROR: Failed to retrieve employees")
        print(f"DEBUG: Error Code: {e.errno}, Message: {e.msg}")
        raise Exception(f"Failed to retrieve employees: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            close_connection(connection)


def update_employee(employee_id: int, employee_data: EmployeeUpdate) -> Optional[Dict[str, Any]]:
    """
    Update an existing employee's information.
    
    This function supports partial updates - only fields that are provided
    will be updated.
    
    Args:
        employee_id: The ID of the employee to update
        employee_data: EmployeeUpdate object with fields to update
        
    Returns:
        dict: Updated employee data if successful, None if employee not found
    """
    connection = None
    cursor = None
    
    try:
        # First check if employee exists
        existing_employee = get_employee(employee_id)
        if not existing_employee:
            print(f"DEBUG: Cannot update - employee with ID {employee_id} not found")
            return None
        
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Build dynamic UPDATE query based on provided fields
        update_fields = []
        values = []
        
        # Check each field and add to update if provided
        if employee_data.name is not None:
            update_fields.append("name = %s")
            values.append(employee_data.name)
            
        if employee_data.email is not None:
            update_fields.append("email = %s")
            values.append(employee_data.email)
            
        if employee_data.department is not None:
            update_fields.append("department = %s")
            values.append(employee_data.department)
            
        if employee_data.salary is not None:
            update_fields.append("salary = %s")
            values.append(employee_data.salary)
        
        # If no fields to update, return existing employee
        if not update_fields:
            print("DEBUG: No fields to update")
            return existing_employee
        
        # Add employee_id to values
        values.append(employee_id)
        
        # Construct and execute UPDATE query
        update_query = f"UPDATE employees SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(update_query, tuple(values))
        connection.commit()
        
        print(f"DEBUG: Updated employee with ID: {employee_id}")
        
        # Fetch and return updated employee
        if cursor:
            cursor.close()
        if connection:
            close_connection(connection)
            
        return get_employee(employee_id)
        
    except Error as e:
        print(f"ERROR: Failed to update employee")
        print(f"DEBUG: Error Code: {e.errno}, Message: {e.msg}")
        
        if e.errno == 1062:
            raise Exception("Email already exists in the database")
            
        raise Exception(f"Failed to update employee: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            close_connection(connection)


def delete_employee(employee_id: int) -> bool:
    """
    Delete an employee from the database.
    
    Args:
        employee_id: The ID of the employee to delete
        
    Returns:
        bool: True if employee was deleted, False if not found
    """
    connection = None
    cursor = None
    
    try:
        # First check if employee exists
        existing_employee = get_employee(employee_id)
        if not existing_employee:
            print(f"DEBUG: Cannot delete - employee with ID {employee_id} not found")
            return False
        
        connection = get_connection()
        cursor = connection.cursor()
        
        # SQL DELETE query
        delete_query = "DELETE FROM employees WHERE id = %s"
        cursor.execute(delete_query, (employee_id,))
        connection.commit()
        
        # Check if any row was affected
        if cursor.rowcount > 0:
            print(f"DEBUG: Deleted employee with ID: {employee_id}")
            return True
        else:
            return False
            
    except Error as e:
        print(f"ERROR: Failed to delete employee")
        print(f"DEBUG: Error Code: {e.errno}, Message: {e.msg}")
        raise Exception(f"Failed to delete employee: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            close_connection(connection)


def search_employees_by_department(department: str) -> List[Dict[str, Any]]:
    """
    Search for employees in a specific department.
    
    This is a utility function demonstrating use of loops and conditionals.
    
    Args:
        department: The department name to search for
        
    Returns:
        list: List of employees in the specified department
    """
    connection = None
    cursor = None
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # SQL SELECT with LIKE for flexible matching
        search_query = "SELECT id, name, email, department, salary FROM employees WHERE department LIKE %s"
        cursor.execute(search_query, (f"%{department}%",))
        
        results = cursor.fetchall()
        
        # Process results using loop
        processed_results = []
        for employee in results:
            # Convert Decimal to float
            employee['salary'] = float(employee['salary'])
            processed_results.append(employee)
        
        print(f"DEBUG: Found {len(processed_results)} employees in department matching '{department}'")
        return processed_results
        
    except Error as e:
        print(f"ERROR: Failed to search employees")
        print(f"DEBUG: Error Code: {e.errno}, Message: {e.msg}")
        raise Exception(f"Failed to search employees: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            close_connection(connection)
