# utilities.py

from datetime import datetime, timedelta
import re

def generate_id(prefix, last_id):
    """Generate new ID with prefix (e.g., BK-001, MEM-001)"""
    if last_id:
        # Extract number from last ID (e.g., BK-001 -> 1)
        num = int(last_id.split('-')[1])
        new_num = num + 1
    else:
        new_num = 1

    return f"{prefix}-{new_num:03d}"


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_mobile(mobile):
    """Validate mobile number format"""
    # Philippine mobile format: +63 9XX XXX XXXX
    pattern = r'^\+63\s9\d{2}\s\d{3}\s\d{4}$'
    return re.match(pattern, mobile) is not None


def calculate_fine(due_date, return_date, daily_rate=50):
    """Calculate fine for overdue books (₱50 per day)"""
    if not return_date:
        return_date = datetime.now().date()

    if isinstance(due_date, str):
        due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
    if isinstance(return_date, str):
        return_date = datetime.strptime(return_date, '%Y-%m-%d').date()

    days_overdue = (return_date - due_date).days

    if days_overdue > 0:
        return days_overdue * daily_rate
    return 0


def format_date(date_obj):
    """Format date to MM-DD-YY"""
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
    return date_obj.strftime('%m-%d-%y')


def format_currency(amount):
    """Format amount to Philippine Peso"""
    return f"₱{amount:,.2f}"


def calculate_due_date(borrow_date, borrowing_period=14):
    """Calculate due date (default 14 days from borrow date)"""
    if isinstance(borrow_date, str):
        borrow_date = datetime.strptime(borrow_date, '%Y-%m-%d').date()

    due_date = borrow_date + timedelta(days=borrowing_period)
    return due_date


def validate_isbn(isbn):
    """Validate ISBN format (basic validation)"""
    # Remove hyphens and spaces
    isbn = isbn.replace('-', '').replace(' ', '')

    # Check if it's 10 or 13 digits
    return len(isbn) in [10, 13] and isbn.isdigit()