# main_system.py

import tkinter as tk
from tkinter import messagebox
from configuration import APP_TITLE, APP_GEOMETRY, COLORS
from database import Database
from authentication import AuthPage
from dashboard import Dashboard


class LibraryManagementSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry(APP_GEOMETRY)
        self.root.configure(bg=COLORS['background'])

        # Center window on screen
        self.center_window()

        # Initialize database
        self.db = Database()

        # Setup database
        self.setup_database()

        # Show authentication page
        self.show_auth_page()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_database(self):
        """Initialize database and tables"""
        try:
            # Create database if not exists
            self.db.create_database()

            # Connect to database
            if not self.db.connect():
                messagebox.showerror(
                    "Database Error",
                    "Failed to connect to database. Please check your MySQL configuration."
                )
                self.root.destroy()
                return

            # Create tables
            self.db.create_tables()

            # Insert default librarian
            self.db.insert_default_librarian()

        except Exception as e:
            messagebox.showerror(
                "Setup Error",
                f"Error setting up database: {str(e)}"
            )
            self.root.destroy()

    def show_auth_page(self):
        """Display authentication page"""
        auth = AuthPage(self.root, self.db, self.show_dashboard)
        auth.show()

    def show_dashboard(self):
        """Display main dashboard"""
        dashboard = Dashboard(self.root, self.db)
        dashboard.show()

    def run(self):
        """Start the application"""
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start main loop
        self.root.mainloop()

    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.db.close()
            self.root.destroy()

def main():
    """Main entry point"""
    app = LibraryManagementSystem()
    app.run()

if __name__ == "__main__":
    main()