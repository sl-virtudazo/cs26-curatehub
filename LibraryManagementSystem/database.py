import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish database connection"""
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
        """Create database if not exists"""
        try:
            conn = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password']
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            cursor.close()
            conn.close()
            print("Database created successfully")
        except Error as e:
            print(f"Error creating database: {e}")

    def create_tables(self):
        """Create all required tables"""
        tables = [
            # Librarian table for authentication
            """
            CREATE TABLE IF NOT EXISTS librarians (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Books table
            """
            CREATE TABLE IF NOT EXISTS books (
                book_id VARCHAR(20) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                isbn VARCHAR(20) UNIQUE,
                category VARCHAR(100),
                status ENUM('Available', 'Borrowed') DEFAULT 'Available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Members table
            """
            CREATE TABLE IF NOT EXISTS members (
                member_id VARCHAR(20) PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                mobile_number VARCHAR(20),
                status ENUM('Active', 'Inactive') DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Borrowed books table
            """
            CREATE TABLE IF NOT EXISTS borrowed_books (
                borrow_id INT AUTO_INCREMENT PRIMARY KEY,
                book_id VARCHAR(20),
                member_id VARCHAR(20),
                borrow_date DATE NOT NULL,
                due_date DATE NOT NULL,
                return_date DATE,
                status ENUM('Borrowed', 'Returned', 'Overdue', 'Lost') DEFAULT 'Borrowed',
                fine_amount DECIMAL(10, 2) DEFAULT 0.00,
                FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
                FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE
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
        """Insert default librarian account"""
        query = """
        INSERT IGNORE INTO librarians (username, password, email)
        VALUES ('admin', 'admin123', 'admin@library.com')
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("Default librarian created (username: admin, password: admin123)")
        except Error as e:
            print(f"Error creating default librarian: {e}")

    def execute_query(self, query, params=None):
        """Execute a query with optional parameters"""
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
        """Fetch all results from a query"""
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
        """Fetch one result from a query"""
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
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed")
