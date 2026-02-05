"""
db.py - MySQL Database Connection Module

This module handles the MySQL database connection using mysql-connector-python.
It provides functions to establish and manage database connections with proper
error handling for debugging and stability.
"""

import mysql.connector
from mysql.connector import Error
from typing import Optional
import os


# Database configuration - Reads from environment variables with fallbacks
# This allows the same code to work locally and in Docker
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root"),
    "database": os.getenv("DB_NAME", "employee_db")
}


def get_connection() -> Optional[mysql.connector.MySQLConnection]:
    """
    Establish and return a MySQL database connection.
    
    This function creates a new connection to the MySQL database using
    the configuration defined in DB_CONFIG. It includes error handling
    to catch and report connection failures.
    
    Returns:
        MySQLConnection: A connection object if successful, None otherwise
        
    Raises:
        Exception: Re-raises the exception after logging for debugging
    """
    connection = None
    try:
        # Attempt to establish database connection
        connection = mysql.connector.connect(**DB_CONFIG)
        
        # Verify connection is active
        if connection.is_connected():
            print(f"DEBUG: Successfully connected to MySQL database '{DB_CONFIG['database']}'")
            return connection
            
    except Error as e:
        # Handle specific MySQL errors for better debugging
        print(f"ERROR: Failed to connect to MySQL database")
        print(f"DEBUG: Error Code: {e.errno}")
        print(f"DEBUG: Error Message: {e.msg}")
        
        # Common error codes and their meanings
        if e.errno == 1045:
            print("DEBUG: Access denied - Check username and password")
        elif e.errno == 1049:
            print("DEBUG: Unknown database - Make sure 'employee_db' exists")
        elif e.errno == 2003:
            print("DEBUG: Can't connect to server - Is MySQL running?")
        
        raise Exception(f"Database connection failed: {e}")
    
    return connection


def close_connection(connection: mysql.connector.MySQLConnection) -> None:
    """
    Safely close the database connection.
    
    Args:
        connection: The MySQL connection to close
    """
    try:
        if connection and connection.is_connected():
            connection.close()
            print("DEBUG: Database connection closed successfully")
    except Error as e:
        print(f"WARNING: Error while closing connection: {e}")


def test_connection() -> bool:
    """
    Test if database connection can be established.
    
    This utility function is useful for health checks and debugging.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        conn = get_connection()
        if conn:
            close_connection(conn)
            return True
    except Exception as e:
        print(f"DEBUG: Connection test failed: {e}")
    return False


# Initialize database and table if they don't exist
def init_database() -> None:
    """
    Initialize the database and create the employees table if it doesn't exist.
    
    This function should be called when the application starts to ensure
    the required database structure is in place.
    """
    try:
        # First connect without specifying database to create it if needed
        temp_config = DB_CONFIG.copy()
        temp_config.pop("database")
        
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"DEBUG: Database '{DB_CONFIG['database']}' is ready")
        
        cursor.close()
        connection.close()
        
        # Now connect to the database and create table
        connection = get_connection()
        cursor = connection.cursor()
        
        # Create employees table if it doesn't exist
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            department VARCHAR(50) NOT NULL,
            salary DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_sql)
        connection.commit()
        print("DEBUG: Employees table is ready")
        
        cursor.close()
        close_connection(connection)
        
    except Error as e:
        print(f"ERROR: Failed to initialize database: {e}")
        raise Exception(f"Database initialization failed: {e}")
