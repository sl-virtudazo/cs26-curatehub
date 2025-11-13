# database.py

import mysql.connector
from mysql.connector import Error
from configuration import DB_CONFIG

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        # Establish database connection
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor(dictionary=True)
            print("Database connected successfully")
            print(f"Connected to database: {DB_CONFIG['database']}")
            return True
        except Error as e:
            print(f"Error connecting to database: {e}")
            return False

    @staticmethod
    def create_database():
        # Create database if not exists
        try:
            conn = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'])
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            cursor.close()
            conn.close()
            print("Database created successfully")
        except Error as e:
            print(f"Error creating database: {e}")

    def create_tables(self):
        # Create all required tables
        tables = [
            # Librarians table
            """
            CREATE TABLE IF NOT EXISTS librarians (
                librarian_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Members table
            """
            CREATE TABLE IF NOT EXISTS members (
                member_id VARCHAR(15) PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                mobile_number VARCHAR(20),
                status ENUM('Active', 'Inactive') DEFAULT 'Active' NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            # Books table
            """
            CREATE TABLE IF NOT EXISTS books (
                book_id VARCHAR(15) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(100) NOT NULL,
                isbn VARCHAR(20) UNIQUE NOT NULL,
                category VARCHAR(100) NOT NULL,
                status ENUM('Available', 'Borrowed') DEFAULT 'Available' NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            # Borrowed books table
            """
            CREATE TABLE IF NOT EXISTS borrowed_books (
                borrow_id INT AUTO_INCREMENT PRIMARY KEY,
                book_id VARCHAR(15) NOT NULL,
                member_id VARCHAR(15) NOT NULL,
                borrow_date DATE NOT NULL,
                due_date DATE NOT NULL,
                return_date DATE,
                status ENUM('Borrowed', 'Returned', 'Overdue') NOT NULL DEFAULT 'Borrowed',
                fine_amount DECIMAL(10, 2) DEFAULT 0.00,
                FOREIGN KEY (book_id) REFERENCES books(book_id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (member_id) REFERENCES members(member_id) ON UPDATE CASCADE DELETE CASCADE
            )
            """
        ]

        try:
            for table in tables:
                self.cursor.execute(table)
            self.connection.commit()
            print("Tables created successfully")
        except Error as e:
            print(f"Error creating tables: {e}")

    def insert_default_librarian(self):
        # Insert default librarian account
        query = """
        INSERT IGNORE INTO librarians (username, password)
        VALUES ('slvirtudazo', '554893')
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("Default librarian created (username: slvirtudazo, password: 554893)")
        except Error as e:
            print(f"Error creating default librarian: {e}")

    def execute_query(self, query, params=None):
        # Execute a query with optional parameters
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Error as e:
            print(f"Query error: {e}")
            return False

    def fetch_all(self, query, params=None):
        # Fetch all results from a query
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Fetch error: {e}")
            return []

    def fetch_one(self, query, params=None):
        # Fetch one result from a query
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Error as e:
            print(f"Fetch error: {e}")
            return None

    def close(self):
        # Close database connection
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed")