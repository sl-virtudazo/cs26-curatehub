# config.py
# Configuration file for theme colors and database settings

# Theme Colors
COLORS = {
    'primary': '#4A4A32',      # Olive Charcoal
    'secondary': '#8B7E66',    # Muted Taupe
    'background': '#F4F1EA',   # Creamy Beige
    'accent': '#A67B5B',       # Warm Brown
    'text': '#2E2E2E'          # Deep Graphite
}

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Set your MySQL password
    'database': 'db_library'
}

# Application Settings
APP_TITLE = "Library Management System"
APP_GEOMETRY = "1200x700"

# Font Styles - Updated to requested fonts
FONTS = {
    'title': ('Segoe UI', 25, 'bold'),        # Main titles
    'heading': ('Open Sans', 15, 'bold'),     # Main texts (bold for headings)
    'subheading': ('Open Sans', 15),          # Main texts (normal)
    'normal': ('Open Sans', 15),              # Main texts
    'small': ('Garamond', 12),                # Sub texts
    'subtext': ('Garamond', 12, 'italic'),
    'pass': ('Garamond', 11),
    'login': ('Segoe UI', 11, 'bold')# Password
}