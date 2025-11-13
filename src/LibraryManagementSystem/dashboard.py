# dashboard.py

import tkinter as tk
from configuration import COLORS, FONTS

class Dashboard:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.current_page = None
        self.main_frame = None
        self.content_frame = None

    def show(self):
        # Display dashboard with sidebar navigation
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        self.main_frame = tk.Frame(self.root, bg=COLORS['background'])
        self.main_frame.pack(fill='both', expand=True)

        # Sidebar
        sidebar = tk.Frame(
            self.main_frame,
            bg=COLORS['primary'],
            width=250)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        # Logo/Title in sidebar
        logo = tk.Label(
            sidebar,
            text="CurateHub",
            font=FONTS['title'],
            bg=COLORS['primary'],
            fg='white')
        logo.pack(pady=30)

        # Navigation buttons
        nav_buttons = [
            ("Catalog Management", self.show_book_management),
            ("Patron Management", self.show_membership_management),
            ("Circulation Desk", self.show_borrowed_management),
            ("Library Reports", self.show_reports_analytics)]

        for text, command in nav_buttons:
            btn = tk.Button(
                sidebar,
                text=text,
                font=FONTS['small'],
                bg=COLORS['primary'],
                fg='white',
                bd=0,
                pady=15,
                cursor='hand2',
                anchor='w',
                padx=20,
                command=command)
            btn.pack(fill='x', pady=2)

            # Hover effects
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=COLORS['secondary']))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=COLORS['primary']))

        # Logout button at bottom
        logout_btn = tk.Button(
            sidebar,
            text="Logout",
            font=FONTS['login'],
            bg=COLORS['accent'],
            fg='white',
            bd=0,
            pady=15,
            cursor='hand2',
            command=self.logout)
        logout_btn.pack(side='bottom', fill='x', pady=20)

        # Hover effect for logout
        logout_btn.bind('<Enter>', lambda e: logout_btn.configure(bg=COLORS['secondary']))
        logout_btn.bind('<Leave>', lambda e: logout_btn.configure(bg=COLORS['accent']))

        # Content area
        self.content_frame = tk.Frame(
            self.main_frame,
            bg=COLORS['background'])
        self.content_frame.pack(side='right', fill='both', expand=True)

        # Show default page (Book Management)
        self.show_book_management()

    def clear_content(self):
        # Clear content area
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_book_management(self):
        # Show book management page
        self.clear_content()
        from catalog_management import BookManagement
        self.current_page = BookManagement(self.content_frame, self.db)
        self.current_page.show()

    def show_membership_management(self):
        # Show membership management page
        self.clear_content()
        from patron_management import MembershipManagement
        self.current_page = MembershipManagement(self.content_frame, self.db)
        self.current_page.show()

    def show_borrowed_management(self):
        # Show borrowed books management page
        self.clear_content()
        from circulation_desk import BorrowedManagement
        self.current_page = BorrowedManagement(self.content_frame, self.db)
        self.current_page.show()

    def show_reports_analytics(self):
        # Show reports and analytics page
        self.clear_content()
        from library_reports import ReportsAnalytics
        self.current_page = ReportsAnalytics(self.content_frame, self.db)
        self.current_page.show()

    def logout(self):
        # Handle logout
        from tkinter import messagebox
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Return to login page
            from authentication import AuthPage
            auth = AuthPage(self.root, self.db, self.show)
            auth.show()