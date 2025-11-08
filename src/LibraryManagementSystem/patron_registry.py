# patron_registry.py

import tkinter as tk
from tkinter import ttk, messagebox
from configuration import COLORS, FONTS
from utilities import generate_id, validate_email, validate_mobile
from datetime import datetime


class MembershipManagement:
    def __init__(self, parent, db):
        self.context_menu = None
        self.parent = parent
        self.db = db
        self.tree = None
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")

    def show(self):
        """Display membership management interface"""
        # Header
        header = tk.Frame(self.parent, bg=COLORS['background'])
        header.pack(fill='x', padx=20, pady=20)

        title = tk.Label(
            header,
            text="Membership Management",
            font=FONTS['heading'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        title.pack(anchor='w')

        subtitle = tk.Label(
            header,
            text="Manage member records, statuses, and registration details",
            font=FONTS['small'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        subtitle.pack(anchor='w')

        # Search and filter frame
        search_frame = tk.Frame(self.parent, bg=COLORS['background'])
        search_frame.pack(fill='x', padx=20, pady=(0, 10))

        # Search bar
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=FONTS['small'],
            width=40
        )
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self.search_members())

        search_btn = tk.Button(
            search_frame,
            text="Search",
            font=FONTS['small'],
            bg=COLORS['primary'],
            fg='white',
            cursor='hand2',
            command=self.search_members
        )
        search_btn.pack(side='left', padx=(0, 20))
        search_btn.bind('<Enter>', lambda e: search_btn.configure(bg=COLORS['secondary']))
        search_btn.bind('<Leave>', lambda e: search_btn.configure(bg=COLORS['primary']))

        # Filter dropdown
        tk.Label(
            search_frame,
            text="Status:",
            font=FONTS['small'],
            bg=COLORS['background'],
            fg=COLORS['text']
        ).pack(side='left')

        filter_combo = ttk.Combobox(
            search_frame,
            textvariable=self.filter_var,
            values=["All", "Active", "Inactive"],
            state='readonly',
            width=15
        )
        filter_combo.pack(side='left', padx=5)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.load_members())

        # Add member button
        add_btn = tk.Button(
            search_frame,
            text="+ Add New Member",
            font=FONTS['small'],
            bg=COLORS['accent'],
            fg='white',
            cursor='hand2',
            command=self.add_member_dialog
        )
        add_btn.pack(side='right')
        add_btn.bind('<Enter>', lambda e: add_btn.configure(bg=COLORS['secondary']))
        add_btn.bind('<Leave>', lambda e: add_btn.configure(bg=COLORS['accent']))

        # Table frame with scrollbars
        table_frame = tk.Frame(self.parent, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')

        columns = ('member_id', 'full_name', 'email', 'mobile_number', 'status', 'borrowed_books', 'added_at',
                   'updated_at')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Define headings and widths
        headings = {
            'member_id': 120, 'full_name': 200, 'email': 220, 'mobile_number': 150,
            'status': 100, 'borrowed_books': 130, 'added_at': 150, 'updated_at': 150
        }
        for col, width in headings.items():
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, width=width)

        self.tree.pack(fill='both', expand=True)

        # Context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="View", command=self.view_member)
        self.context_menu.add_command(label="Update", command=self.update_member_dialog)
        self.context_menu.add_command(label="Delete", command=self.delete_member)
        self.tree.bind('<Button-3>', self.show_context_menu)

        # Load initial data
        self.load_members()

    def show_context_menu(self, event):
        try:
            row_id = self.tree.identify_row(event.y)
            if row_id:
                self.tree.selection_set(row_id)
                self.context_menu.post(event.x_root, event.y_root)
        except tk.TclError:
            pass

    def load_members(self):
        """Load members including borrowed count and timestamps"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        filter_value = self.filter_var.get()
        if filter_value == "All":
            query = """
            SELECT m.*, COUNT(bb.borrow_id) AS borrowed_count
            FROM members m
            LEFT JOIN borrowed_books bb ON m.member_id = bb.member_id AND bb.status = 'Borrowed'
            GROUP BY m.member_id
            ORDER BY m.member_id
            """
            members = self.db.fetch_all(query)
        else:
            query = """
            SELECT m.*, COUNT(bb.borrow_id) AS borrowed_count
            FROM members m
            LEFT JOIN borrowed_books bb ON m.member_id = bb.member_id AND bb.status = 'Borrowed'
            WHERE m.status = %s
            GROUP BY m.member_id
            ORDER BY m.member_id
            """
            members = self.db.fetch_all(query, (filter_value,))

        for member in members:
            added_at = member['added_at'].strftime('%Y-%m-%d %H:%M:%S') if member['added_at'] else ''
            updated_at = member['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if member['updated_at'] else ''
            borrowed_text = f"{member['borrowed_count']} book" if member[
                                                                      'borrowed_count'] == 1 else f"{member['borrowed_count']} books"
            self.tree.insert('', 'end', values=(
                member['member_id'],
                member['full_name'],
                member['email'],
                member['mobile_number'],
                member['status'],
                borrowed_text,
                added_at,
                updated_at
            ))

    def search_members(self):
        """Search members by keyword including timestamps"""
        keyword = self.search_var.get().strip()
        if not keyword:
            self.load_members()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
        SELECT m.*, COUNT(bb.borrow_id) AS borrowed_count
        FROM members m
        LEFT JOIN borrowed_books bb ON m.member_id = bb.member_id AND bb.status = 'Borrowed'
        WHERE m.member_id LIKE %s OR m.full_name LIKE %s OR m.email LIKE %s OR m.mobile_number LIKE %s
        GROUP BY m.member_id
        ORDER BY m.member_id
        """
        search_pattern = f"%{keyword}%"
        members = self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern, search_pattern))

        for member in members:
            added_at = member['added_at'].strftime('%Y-%m-%d %H:%M:%S') if member['added_at'] else ''
            updated_at = member['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if member['updated_at'] else ''
            borrowed_text = f"{member['borrowed_count']} book" if member[
                                                                      'borrowed_count'] == 1 else f"{member['borrowed_count']} books"
            self.tree.insert('', 'end', values=(
                member['member_id'],
                member['full_name'],
                member['email'],
                member['mobile_number'],
                member['status'],
                borrowed_text,
                added_at,
                updated_at
            ))

    def add_member_dialog(self):
        """Add new member dialog with added_at and updated_at"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Member")
        dialog.geometry("500x450")
        dialog.configure(bg='white')
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (450 // 2)
        dialog.geometry(f'500x450+{x}+{y}')

        tk.Label(dialog, text="Add New Member", font=FONTS['heading'], bg='white', fg=COLORS['text']).pack(pady=20)
        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(padx=30, fill='both', expand=True)

        # Fields
        tk.Label(form_frame, text="Full Name*", font=FONTS['small'], bg='white').pack(anchor='w')
        name_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        name_entry.pack(pady=(0, 15))

        tk.Label(form_frame, text="Email*", font=FONTS['small'], bg='white').pack(anchor='w')
        email_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        email_entry.pack(pady=(0, 15))

        tk.Label(form_frame, text="Mobile Number* (+63 9XX XXX XXXX)", font=FONTS['small'], bg='white').pack(anchor='w')
        mobile_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        mobile_entry.pack(pady=(0, 20))

        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(pady=20)

        def save_member():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            mobile = mobile_entry.get().strip()

            if not all([name, email, mobile]):
                messagebox.showerror("Error", "All fields are required", parent=dialog)
                return
            if not validate_email(email):
                messagebox.showerror("Error", "Invalid email format", parent=dialog)
                return
            if not validate_mobile(mobile):
                messagebox.showerror("Error", "Invalid mobile format. Use: +63 9XX XXX XXXX", parent=dialog)
                return

            last_member = self.db.fetch_one("SELECT member_id FROM members ORDER BY member_id DESC LIMIT 1")
            member_id = generate_id("MEM", last_member['member_id'] if last_member else None)
            now = datetime.now()

            query = """
            INSERT INTO members (member_id, full_name, email, mobile_number, status, added_at, updated_at)
            VALUES (%s, %s, %s, %s, 'Active', %s, %s)
            """

            if self.db.execute_query(query, (member_id, name, email, mobile, now, now)):
                messagebox.showinfo("Success", f"Member added successfully! (ID: {member_id})", parent=dialog)
                dialog.destroy()
                self.load_members()
            else:
                messagebox.showerror("Error", "Failed to add member. Email might already exist.", parent=dialog)

        save_btn = tk.Button(btn_frame, text="Save Member", font=FONTS['small'],
                             bg=COLORS['primary'], fg='white', width=15, cursor='hand2', command=save_member)
        save_btn.pack(side='left', padx=5)
        save_btn.bind('<Enter>', lambda e: save_btn.configure(bg=COLORS['secondary']))
        save_btn.bind('<Leave>', lambda e: save_btn.configure(bg=COLORS['primary']))

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=FONTS['small'],
                               bg=COLORS['accent'], fg='white', width=15, cursor='hand2', command=dialog.destroy)
        cancel_btn.pack(side='left', padx=5)
        cancel_btn.bind('<Enter>', lambda e: cancel_btn.configure(bg=COLORS['secondary']))
        cancel_btn.bind('<Leave>', lambda e: cancel_btn.configure(bg=COLORS['accent']))

    def view_member(self):
        """View member details with improved styling matching book details view"""
        selected = self.tree.selection()
        if not selected:
            return

        member_id = self.tree.item(selected[0])['values'][0]
        member = self.db.fetch_one("""
            SELECT m.*, COUNT(bb.borrow_id) AS borrowed_count
            FROM members m
            LEFT JOIN borrowed_books bb 
                ON m.member_id = bb.member_id AND bb.status = 'Borrowed'
            WHERE m.member_id = %s
            GROUP BY m.member_id
        """, (member_id,))
        if not member:
            return

        dialog = tk.Toplevel(self.parent)
        dialog.title("Member Details")
        dialog.geometry("500x400")
        dialog.configure(bg='white')
        dialog.resizable(False, False)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f'500x400+{x}+{y}')

        tk.Label(
            dialog,
            text="Member Details",
            font=FONTS['heading'],
            bg='white',
            fg=COLORS['text']
        ).pack(pady=15)

        details_frame = tk.Frame(dialog, bg='white')
        details_frame.pack(padx=30, pady=10, fill='both', expand=True)

        # Format dates with time
        added_at = member['added_at'].strftime("%Y-%m-%d %H:%M:%S") if member['added_at'] else ""
        updated_at = member['updated_at'].strftime("%Y-%m-%d %H:%M:%S") if member['updated_at'] else ""

        # Format borrowed books text
        borrowed_count = member['borrowed_count'] or 0
        borrowed_text = f"{borrowed_count} book" if borrowed_count == 1 else f"{borrowed_count} books"

        # Member details in structured format
        details = [
            ("Member ID:", member['member_id']),
            ("Full Name:", member['full_name']),
            ("Email:", member['email']),
            ("Mobile Number:", member['mobile_number']),
            ("Status:", member['status']),
            ("Borrowed Books:", borrowed_text),
            ("Added At:", added_at),
            ("Updated At:", updated_at)
        ]

        for label, value in details:
            row = tk.Frame(details_frame, bg='white')
            row.pack(fill='x', pady=2)

            tk.Label(
                row,
                text=label,
                font=FONTS['small'],
                bg='white',
                fg=COLORS['text'],
                width=15,
                anchor='w'
            ).pack(side='left')

            tk.Label(
                row,
                text=value,
                font=FONTS['small'],
                bg='white',
                fg=COLORS['text'],
                anchor='w'
            ).pack(side='left', fill='x', expand=True)

        close_btn = tk.Button(
            dialog,
            text="Close",
            font=FONTS['small'],
            bg=COLORS['primary'],
            fg='white',
            width=10,
            command=dialog.destroy
        )
        close_btn.pack(pady=10)

        # Hover effect
        close_btn.bind('<Enter>', lambda e: close_btn.configure(bg=COLORS['secondary']))
        close_btn.bind('<Leave>', lambda e: close_btn.configure(bg=COLORS['primary']))

    def update_member_dialog(self):
        """Show update member dialog"""
        selected = self.tree.selection()
        if not selected:
            return

        member_id = self.tree.item(selected[0])['values'][0]
        member = self.db.fetch_one("SELECT * FROM members WHERE member_id = %s", (member_id,))

        if not member:
            return

        dialog = tk.Toplevel(self.parent)
        dialog.title("Update Member")
        dialog.geometry("500x450")
        dialog.configure(bg='white')
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (450 // 2)
        dialog.geometry(f'500x450+{x}+{y}')

        tk.Label(dialog, text="Update Member", font=FONTS['heading'], bg='white', fg=COLORS['text']).pack(pady=20)
        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(padx=30, fill='both', expand=True)

        tk.Label(form_frame, text="Full Name*", font=FONTS['small'], bg='white').pack(anchor='w')
        name_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        name_entry.insert(0, member['full_name'])
        name_entry.pack(pady=(0, 15))

        tk.Label(form_frame, text="Email*", font=FONTS['small'], bg='white').pack(anchor='w')
        email_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        email_entry.insert(0, member['email'])
        email_entry.pack(pady=(0, 15))

        tk.Label(form_frame, text="Mobile Number*", font=FONTS['small'], bg='white').pack(anchor='w')
        mobile_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        mobile_entry.insert(0, member['mobile_number'])
        mobile_entry.pack(pady=(0, 15))

        # Status field - NEW ADDITION
        tk.Label(form_frame, text="Status*", font=FONTS['small'], bg='white').pack(anchor='w')
        status_var = tk.StringVar(value=member['status'])
        status_combo = ttk.Combobox(
            form_frame,
            textvariable=status_var,
            values=["Active", "Inactive"],
            state='readonly',
            width=37
        )
        status_combo.pack(pady=(0, 20))

        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(pady=20)

        def update_member():
            full_name = name_entry.get().strip()
            email = email_entry.get().strip()
            mobile_number = mobile_entry.get().strip()
            status = status_var.get()  # Get the selected status

            if not all([full_name, email, mobile_number, status]):
                messagebox.showerror("Error", "All fields are required", parent=dialog)
                return

            now = datetime.now()
            query = """
            UPDATE members 
            SET full_name = %s, email = %s, mobile_number = %s, status = %s, updated_at = %s
            WHERE member_id = %s
            """
            if self.db.execute_query(query, (full_name, email, mobile_number, status, now, member_id)):
                messagebox.showinfo("Success", "Member updated successfully!", parent=dialog)
                dialog.destroy()
                self.load_members()  # Refresh the member list
            else:
                messagebox.showerror("Error", "Failed to update member", parent=dialog)

        update_btn = tk.Button(btn_frame, text="Update Member", font=FONTS['small'], bg=COLORS['primary'],
                               fg='white', width=15, cursor='hand2', command=update_member)
        update_btn.pack(side='left', padx=5)
        update_btn.bind('<Enter>', lambda e: update_btn.configure(bg=COLORS['secondary']))
        update_btn.bind('<Leave>', lambda e: update_btn.configure(bg=COLORS['primary']))

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=FONTS['small'], bg=COLORS['accent'],
                               fg='white', width=15, cursor='hand2', command=dialog.destroy)
        cancel_btn.pack(side='left', padx=5)
        cancel_btn.bind('<Enter>', lambda e: cancel_btn.configure(bg=COLORS['secondary']))
        cancel_btn.bind('<Leave>', lambda e: cancel_btn.configure(bg=COLORS['accent']))

    def delete_member(self):
        """Delete member with confirmation"""
        selected = self.tree.selection()
        if not selected:
            return
        member_id = self.tree.item(selected[0])['values'][0]
        member_name = self.tree.item(selected[0])['values'][1]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete member '{member_name}'?"):
            query = "DELETE FROM members WHERE member_id=%s"
            if self.db.execute_query(query, (member_id,)):
                messagebox.showinfo("Success", "Member deleted successfully!")
                self.load_members()
            else:
                messagebox.showerror("Error", "Failed to delete member")