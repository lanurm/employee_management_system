"""
models.py - Employee class definition using OOP principles

This module contains the Employee class that represents an employee entity
with attributes like id, name, email, department, and salary.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Employee:
    """
    Employee class representing an employee in the organization.
    
    This class uses OOP principles including:
    - Encapsulation: Attributes are accessed via properties
    - Methods: Includes utility methods for data manipulation
    
    Attributes:
        id (int): Unique identifier for the employee
        name (str): Full name of the employee
        email (str): Email address of the employee
        department (str): Department where employee works
        salary (float): Monthly salary of the employee
    """
    
    def __init__(self, id: int, name: str, email: str, department: str, salary: float):
        """Initialize an Employee instance with the given attributes."""
        self._id = id
        self._name = name
        self._email = email
        self._department = department
        self._salary = salary
    
    # Properties for encapsulation
    @property
    def id(self) -> int:
        """Get the employee ID."""
        return self._id
    
    @property
    def name(self) -> str:
        """Get the employee name."""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Set the employee name."""
        self._name = value
    
    @property
    def email(self) -> str:
        """Get the employee email."""
        return self._email
    
    @email.setter
    def email(self, value: str):
        """Set the employee email."""
        self._email = value
    
    @property
    def department(self) -> str:
        """Get the employee department."""
        return self._department
    
    @department.setter
    def department(self, value: str):
        """Set the employee department."""
        self._department = value
    
    @property
    def salary(self) -> float:
        """Get the employee salary."""
        return self._salary
    
    @salary.setter
    def salary(self, value: float):
        """Set the employee salary."""
        if value < 0:
            raise ValueError("Salary cannot be negative")
        self._salary = value
    
    def to_dict(self) -> dict:
        """
        Convert Employee object to dictionary.
        
        Returns:
            dict: Dictionary representation of the employee
        """
        return {
            "id": self._id,
            "name": self._name,
            "email": self._email,
            "department": self._department,
            "salary": self._salary
        }
    
    def __str__(self) -> str:
        """Return string representation of the employee."""
        return f"Employee(id={self._id}, name='{self._name}', department='{self._department}')"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"Employee(id={self._id}, name='{self._name}', email='{self._email}', department='{self._department}', salary={self._salary})"


# Pydantic models for API request/response validation
class EmployeeCreate(BaseModel):
    """
    Pydantic model for creating a new employee.
    Used for validating POST request data.
    """
    name: str = Field(..., min_length=1, max_length=100, description="Employee full name")
    email: str = Field(..., description="Employee email address")
    department: str = Field(..., min_length=1, max_length=50, description="Department name")
    salary: float = Field(..., gt=0, description="Monthly salary (must be positive)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@company.com",
                "department": "Engineering",
                "salary": 75000.00
            }
        }


class EmployeeUpdate(BaseModel):
    """
    Pydantic model for updating an existing employee.
    All fields are optional to allow partial updates.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None)
    department: Optional[str] = Field(None, min_length=1, max_length=50)
    salary: Optional[float] = Field(None, gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Smith",
                "salary": 80000.00
            }
        }


class EmployeeResponse(BaseModel):
    """
    Pydantic model for employee API responses.
    Includes all employee attributes.
    """
    id: int
    name: str
    email: str
    department: str
    salary: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@company.com",
                "department": "Engineering",
                "salary": 75000.00
            }
        }
