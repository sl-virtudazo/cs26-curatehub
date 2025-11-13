# circulation_desk.py

import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

from configuration import COLORS, FONTS
from utilities import format_currency, calculate_due_date


class BorrowedManagement:
    def __init__(self, parent, db):
        self.context_menu = None
        self.parent = parent
        self.db = db
        self.tree = None
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")

    def show(self):
        """Display borrowed books management interface"""
        # Header
        header = tk.Frame(self.parent, bg=COLORS['background'])
        header.pack(fill='x', padx=20, pady=20)

        title = tk.Label(
            header,
            text="Circulation Desk",
            font=FONTS['heading'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        title.pack(anchor='w')

        subtitle = tk.Label(
            header,
            text="Monitor book loans, returns, and overdue borrowings",
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
        search_entry.bind('<Return>', lambda e: self.search_borrowed())

        search_btn = tk.Button(
            search_frame,
            text="Search",
            font=FONTS['small'],
            bg=COLORS['primary'],
            fg='white',
            cursor='hand2',
            command=self.search_borrowed
        )
        search_btn.pack(side='left', padx=(0, 20))

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
            values=["All", "Borrowed", "Returned", "Overdue", "Lost"],
            state='readonly',
            width=15
        )
        filter_combo.pack(side='left', padx=5)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.load_borrowed())

        # Add borrowed book button
        add_btn = tk.Button(
            search_frame,
            text="+ Add Borrowed Book",
            font=FONTS['small'],
            bg=COLORS['accent'],
            fg='white',
            cursor='hand2',
            command=self.add_borrowed_dialog
        )
        add_btn.pack(side='right')

        # Table frame
        table_frame = tk.Frame(self.parent, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side='right', fill='y')

        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')

        # Treeview
        columns = ('book_id', 'member_id', 'book_title', 'borrow_date', 'return_date', 'due_date', 'status',
                   'fine_amount', 'updated_at')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Define headings
        self.tree.heading('book_id', text='Book ID')
        self.tree.heading('member_id', text='Member ID')
        self.tree.heading('book_title', text='Book Title')
        self.tree.heading('borrow_date', text='Borrow Date')
        self.tree.heading('return_date', text='Return Date')
        self.tree.heading('due_date', text='Due Date')
        self.tree.heading('status', text='Status')
        self.tree.heading('fine_amount', text='Fine Amount')
        self.tree.heading('updated_at', text='Updated At')

        # Define column widths
        self.tree.column('book_id', width=100)
        self.tree.column('member_id', width=120)
        self.tree.column('book_title', width=200)
        self.tree.column('borrow_date', width=120)
        self.tree.column('return_date', width=120)
        self.tree.column('due_date', width=120)
        self.tree.column('status', width=100)
        self.tree.column('fine_amount', width=120)
        self.tree.column('updated_at', width=160)

        self.tree.pack(fill='both', expand=True)

        # Right-click menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="View Details", command=self.view_borrowed)
        self.context_menu.add_command(label="Update Details", command=self.update_borrowed_dialog)
        self.context_menu.add_command(label="Delete Book", command=self.delete_borrowed)

        self.tree.bind('<Button-3>', self.show_context_menu)

        # Load initial data
        self.load_borrowed()
        self.update_overdue_status()

    def show_context_menu(self, event):
        """Show right-click context menu"""
        try:
            row_id = self.tree.identify_row(event.y)
            if row_id:
                self.tree.selection_set(row_id)
                self.context_menu.post(event.x_root, event.y_root)
        except tk.TclError:
            pass

    def update_overdue_status(self):
        """Update overdue and lost book fines"""

        overdue_query = """
        UPDATE borrowed_books 
        SET status = 'Overdue',
            fine_amount = DATEDIFF(CURDATE(), due_date) * 100,
            updated_at = NOW()
        WHERE status = 'Borrowed' AND due_date < CURDATE()
        """
        self.db.execute_query(overdue_query)

        lost_query = """
        UPDATE borrowed_books 
        SET fine_amount = 1000,
            updated_at = NOW()
        WHERE status = 'Lost' AND (fine_amount IS NULL OR fine_amount = 0)
        """
        self.db.execute_query(lost_query)

    def load_borrowed(self):
        """Load borrowed books from database ordered by due date"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        filter_value = self.filter_var.get()

        if filter_value == "All":
            query = """
            SELECT bb.*, b.title as book_title
            FROM borrowed_books bb
            JOIN books b ON bb.book_id = b.book_id
            ORDER BY bb.due_date ASC
            """
            borrowed = self.db.fetch_all(query)
        else:
            query = """
            SELECT bb.*, b.title as book_title
            FROM borrowed_books bb
            JOIN books b ON bb.book_id = b.book_id
            WHERE bb.status = %s
            ORDER BY bb.due_date ASC
            """
            borrowed = self.db.fetch_all(query, (filter_value,))

        for item in borrowed:
            return_date = item['return_date'].strftime('%Y-%m-%d') if item['return_date'] else 'N/A'
            updated_at = item['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if item.get('updated_at') else ''

            self.tree.insert('', 'end', values=(
                item['book_id'],
                item['member_id'],
                item['book_title'],
                item['borrow_date'].strftime('%Y-%m-%d'),
                return_date,
                item['due_date'].strftime('%Y-%m-%d'),
                item['status'],
                format_currency(item['fine_amount']),
                updated_at
            ))

    def search_borrowed(self):
        """Search borrowed books by keyword"""
        keyword = self.search_var.get().strip()

        if not keyword:
            self.load_borrowed()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
        SELECT bb.*, b.title as book_title
        FROM borrowed_books bb
        JOIN books b ON bb.book_id = b.book_id
        WHERE bb.book_id LIKE %s OR bb.member_id LIKE %s OR b.title LIKE %s
        ORDER BY bb.due_date ASC
        """
        search_pattern = f"%{keyword}%"
        borrowed = self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern))

        for item in borrowed:
            return_date = item['return_date'].strftime('%Y-%m-%d') if item['return_date'] else 'N/A'
            updated_at = item['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if item.get('updated_at') else ''

            self.tree.insert('', 'end', values=(
                item['book_id'],
                item['member_id'],
                item['book_title'],
                item['borrow_date'].strftime('%Y-%m-%d'),
                return_date,
                item['due_date'].strftime('%Y-%m-%d'),
                item['status'],
                format_currency(item['fine_amount']),
                updated_at
            ))

    def add_borrowed_dialog(self):
        """Show add borrowed book dialog with consistent styling"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Issue Book")
        dialog.geometry("500x450")
        dialog.configure(bg='white')
        dialog.resizable(False, False)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (450 // 2)
        dialog.geometry(f'500x450+{x}+{y}')

        tk.Label(
            dialog,
            text="Issue Book",
            font=FONTS['heading'],
            bg='white',
            fg=COLORS['text']
        ).pack(pady=20)

        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(padx=30, pady=(0, 20), fill='both', expand=True)

        # Book ID field
        tk.Label(form_frame, text="Book ID*", font=FONTS['small'], bg='white', anchor='w').pack(fill='x')
        book_id_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        book_id_entry.pack(pady=(0, 15), fill='x')

        # Member ID field
        tk.Label(form_frame, text="Member ID*", font=FONTS['small'], bg='white', anchor='w').pack(fill='x')
        member_id_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        member_id_entry.pack(pady=(0, 15), fill='x')

        # Borrowing period field
        tk.Label(form_frame, text="Borrowing Period (days)*", font=FONTS['small'], bg='white', anchor='w').pack(
            fill='x')
        period_frame = tk.Frame(form_frame, bg='white')
        period_frame.pack(fill='x', pady=(0, 15))
        period_spinbox = tk.Spinbox(period_frame, from_=1, to=30, font=FONTS['small'], width=10)
        period_spinbox.delete(0, 'end')
        period_spinbox.insert(0, '14')
        period_spinbox.pack(side='left')

        # Buttons
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(pady=(10, 20))

        def issue_book():
            book_id = book_id_entry.get().strip()
            member_id = member_id_entry.get().strip()
            period = period_spinbox.get()

            if not all([book_id, member_id, period]):
                messagebox.showerror("Error", "All fields are required", parent=dialog)
                return

            # Check if book exists and is available
            book = self.db.fetch_one("SELECT * FROM books WHERE book_id = %s", (book_id,))
            if not book:
                messagebox.showerror("Error", "Book ID not found", parent=dialog)
                return

            if book['status'] != 'Available':
                messagebox.showerror("Error", "Book is not available for borrowing", parent=dialog)
                return

            # Check if member exists
            member = self.db.fetch_one("SELECT * FROM members WHERE member_id = %s", (member_id,))
            if not member:
                messagebox.showerror("Error", "Member ID not found", parent=dialog)
                return

            # ACTIVATE INACTIVE MEMBER - NEW FUNCTIONALITY
            now = datetime.now()
            if member['status'] == 'Inactive':
                # Update member status to Active
                update_status_query = """
                UPDATE members 
                SET status = 'Active', updated_at = %s 
                WHERE member_id = %s
                """
                self.db.execute_query(update_status_query, (now, member_id))
                messagebox.showinfo("Member Status Updated",
                                    f"Member {member_id} has been activated for borrowing",
                                    parent=dialog)

            # Calculate dates
            borrow_date = datetime.now().date()
            due_date = calculate_due_date(borrow_date, int(period))

            # Insert borrowed record — include updated_at
            query = """
            INSERT INTO borrowed_books (book_id, member_id, borrow_date, due_date, status, updated_at)
            VALUES (%s, %s, %s, %s, 'Borrowed', %s)
            """

            if self.db.execute_query(query, (book_id, member_id, borrow_date, due_date, now)):
                # Update book status
                self.db.execute_query("UPDATE books SET status = 'Borrowed', updated_at = %s WHERE book_id = %s",
                                      (now, book_id))

                messagebox.showinfo("Success",
                                    f"Book issued successfully!\nDue Date: {due_date.strftime('%Y-%m-%d')}",
                                    parent=dialog)
                dialog.destroy()
                # Refresh all relevant tables in the dashboard
                self.load_borrowed()
                # Note: Other dashboard sections should refresh when they're accessed again
            else:
                messagebox.showerror("Error", "Failed to issue book", parent=dialog)

        issue_btn = tk.Button(
            btn_frame,
            text="Issue Book",
            font=FONTS['small'],
            bg=COLORS['primary'],
            fg='white',
            width=12,
            cursor='hand2',
            command=issue_book
        )
        issue_btn.pack(side='left', padx=5)

        # Hover effects
        issue_btn.bind('<Enter>', lambda e: issue_btn.configure(bg=COLORS['secondary']))
        issue_btn.bind('<Leave>', lambda e: issue_btn.configure(bg=COLORS['primary']))

        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=FONTS['small'],
            bg=COLORS['accent'],
            fg='white',
            width=12,
            cursor='hand2',
            command=dialog.destroy
        )
        cancel_btn.pack(side='left', padx=5)

        # Hover effects
        cancel_btn.bind('<Enter>', lambda e: cancel_btn.configure(bg=COLORS['secondary']))
        cancel_btn.bind('<Leave>', lambda e: cancel_btn.configure(bg=COLORS['accent']))

    def view_borrowed(self):
        """View borrowed book details with consistent styling matching membership details"""
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])['values']

        dialog = tk.Toplevel(self.parent)
        dialog.title("Borrowed Book Details")
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
            text="Borrowed Book Details",
            font=FONTS['heading'],
            bg='white',
            fg=COLORS['text']
        ).pack(pady=15)

        details_frame = tk.Frame(dialog, bg='white')
        details_frame.pack(padx=30, pady=10, fill='both', expand=True)

        # Format details in structured rows
        details = [
            ("Book ID:", values[0]),
            ("Member ID:", values[1]),
            ("Book Title:", values[2]),
            ("Borrow Date:", values[3]),
            ("Return Date:", values[4]),
            ("Due Date:", values[5]),
            ("Status:", values[6]),
            ("Fine Amount:", values[7]),
            ("Updated At:", values[8])
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

    def update_borrowed_dialog(self):
        """Show update borrowed book dialog with consistent styling matching membership update"""
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])['values']
        book_id = values[0]
        member_id = values[1]

        # Get borrowed record
        query = """
            SELECT * FROM borrowed_books 
            WHERE book_id = %s AND member_id = %s
            ORDER BY borrow_id DESC LIMIT 1
            """
        borrowed = self.db.fetch_one(query, (book_id, member_id))

        if not borrowed:
            messagebox.showerror("Error", "Borrowed record not found")
            return

        dialog = tk.Toplevel(self.parent)
        dialog.title("Update Borrowed Book")
        dialog.geometry("500x550")
        dialog.configure(bg='white')
        dialog.resizable(False, False)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (550 // 2)
        dialog.geometry(f'500x550+{x}+{y}')

        tk.Label(
            dialog,
            text="Update Borrowed Book",
            font=FONTS['heading'],
            bg='white',
            fg=COLORS['text']
        ).pack(pady=20)

        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(padx=30, pady=(0, 15), fill='both', expand=True)

        # Book ID field
        tk.Label(form_frame, text="Book ID*", font=FONTS['small'], bg='white', anchor='w').pack(fill='x')
        book_id_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        book_id_entry.insert(0, borrowed['book_id'])
        book_id_entry.pack(pady=(0, 15), fill='x')

        # Member ID field
        tk.Label(form_frame, text="Member ID*", font=FONTS['small'], bg='white', anchor='w').pack(fill='x')
        member_id_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        member_id_entry.insert(0, borrowed['member_id'])
        member_id_entry.pack(pady=(0, 15), fill='x')

        # Borrow Date field
        tk.Label(form_frame, text="Borrow Date* (YYYY-MM-DD)", font=FONTS['small'], bg='white', anchor='w').pack(
            fill='x')
        borrow_date_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        borrow_date_entry.insert(0, borrowed['borrow_date'].strftime('%Y-%m-%d'))
        borrow_date_entry.pack(pady=(0, 15), fill='x')

        # Due Date field
        tk.Label(form_frame, text="Due Date* (YYYY-MM-DD)", font=FONTS['small'], bg='white', anchor='w').pack(fill='x')
        due_date_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        due_date_entry.insert(0, borrowed['due_date'].strftime('%Y-%m-%d'))
        due_date_entry.pack(pady=(0, 15), fill='x')

        # Status dropdown
        tk.Label(form_frame, text="Status*", font=FONTS['small'], bg='white', anchor='w').pack(fill='x')
        status_var = tk.StringVar(value=borrowed['status'])
        status_combo = ttk.Combobox(
            form_frame,
            textvariable=status_var,
            values=["Borrowed", "Returned", "Overdue", "Lost"],
            state='readonly',
            width=37
        )
        status_combo.pack(pady=(0, 15), fill='x')

        # Fine Amount field
        tk.Label(form_frame, text="Fine Amount*", font=FONTS['small'], bg='white', anchor='w').pack(fill='x')
        fine_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        fine_entry.insert(0, str(borrowed['fine_amount'] if borrowed['fine_amount'] else "0.00"))
        fine_entry.pack(pady=(0, 15), fill='x')

        # Buttons
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(pady=(10, 20))

        def update_book():
            new_book_id = book_id_entry.get().strip()
            new_member_id = member_id_entry.get().strip()
            borrow_date_str = borrow_date_entry.get().strip()
            due_date_str = due_date_entry.get().strip()
            status = status_combo.get()
            fine_amount = fine_entry.get().strip()

            if not all([new_book_id, new_member_id, borrow_date_str, due_date_str, status, fine_amount]):
                messagebox.showerror("Error", "All fields are required")
                return

            # Validate dates
            try:
                borrow_date = datetime.strptime(borrow_date_str, '%Y-%m-%d').date()
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                fine = float(fine_amount)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format or fine amount")
                return

            # Determine return date based on status
            return_date = None
            if status == "Returned":
                return_date = datetime.now().date()

            now = datetime.now()

            # Update borrowed record
            if return_date:
                update_query = """
                UPDATE borrowed_books 
                SET book_id = %s, member_id = %s, borrow_date = %s, due_date = %s, 
                    status = %s, fine_amount = %s, return_date = %s, updated_at = %s
                WHERE borrow_id = %s
                """
                params = (new_book_id, new_member_id, borrow_date, due_date, status, fine, return_date, now,
                          borrowed['borrow_id'])
            else:
                update_query = """
                UPDATE borrowed_books 
                SET book_id = %s, member_id = %s, borrow_date = %s, due_date = %s, 
                    status = %s, fine_amount = %s, updated_at = %s
                WHERE borrow_id = %s
                """
                params = (new_book_id, new_member_id, borrow_date, due_date, status, fine, now, borrowed['borrow_id'])

            if self.db.execute_query(update_query, params):
                # Update book status if changed to Returned
                if status == "Returned":
                    self.db.execute_query("UPDATE books SET status = 'Available', updated_at = %s WHERE book_id = %s",
                                          (now, new_book_id))

                    # Check if member has any other borrowed books
                    borrowed_count = self.db.fetch_one("""
                        SELECT COUNT(*) as count 
                        FROM borrowed_books 
                        WHERE member_id = %s AND status = 'Borrowed'
                    """, (new_member_id,))

                    # If no other borrowed books, show notification about member status
                    if borrowed_count and borrowed_count['count'] == 0:
                        # Show notification to librarian to manually review member status
                        messagebox.showinfo("Member Status",
                                            f"Member {new_member_id} has no more borrowed books. Consider reviewing their status.",
                                            parent=dialog)
                elif status in ["Borrowed", "Overdue"]:
                    self.db.execute_query("UPDATE books SET status = 'Borrowed', updated_at = %s WHERE book_id = %s",
                                          (now, new_book_id))

                elif status == "Lost":
                    self.db.execute_query("""
                        UPDATE borrowed_books 
                        SET fine_amount = 1000, updated_at = %s 
                        WHERE borrow_id = %s AND (fine_amount IS NULL OR fine_amount = 0)
                    """, (now, borrowed['borrow_id']))
                    self.db.execute_query("UPDATE books SET status = 'Lost', updated_at = %s WHERE book_id = %s",
                                          (now, new_book_id))

                messagebox.showinfo("Success", "Borrowed book updated successfully!")
                dialog.destroy()
                self.load_borrowed()
            else:
                messagebox.showerror("Error", "Failed to update borrowed book")

        update_btn = tk.Button(
            btn_frame,
            text="Update Book",
            font=FONTS['small'],
            bg=COLORS['primary'],
            fg='white',
            width=12,
            cursor='hand2',
            command=update_book
        )
        update_btn.pack(side='left', padx=5)

        # Hover effects
        update_btn.bind('<Enter>', lambda e: update_btn.configure(bg=COLORS['secondary']))
        update_btn.bind('<Leave>', lambda e: update_btn.configure(bg=COLORS['primary']))

        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=FONTS['small'],
            bg=COLORS['accent'],
            fg='white',
            width=12,
            cursor='hand2',
            command=dialog.destroy
        )
        cancel_btn.pack(side='left', padx=5)

        # Hover effects
        cancel_btn.bind('<Enter>', lambda e: cancel_btn.configure(bg=COLORS['secondary']))
        cancel_btn.bind('<Leave>', lambda e: cancel_btn.configure(bg=COLORS['accent']))

    def delete_borrowed(self):
        """Delete borrowed record with confirmation"""
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])['values']
        book_title = values[2]

        if messagebox.askyesno("Confirm Delete",
                               f"Are you sure you want to delete this borrowed record for '{book_title}'?"):
            book_id = values[0]
            member_id = values[1]

            query = """
            DELETE FROM borrowed_books 
            WHERE book_id = %s AND member_id = %s 
            ORDER BY borrow_id DESC LIMIT 1
            """

            if self.db.execute_query(query, (book_id, member_id)):
                # Update book status back to available
                now = datetime.now()
                self.db.execute_query("UPDATE books SET status = 'Available', updated_at = %s WHERE book_id = %s",
                                      (now, book_id))
                messagebox.showinfo("Success", "Borrowed record deleted successfully!")
                self.load_borrowed()
            else:
                messagebox.showerror("Error", "Failed to delete record")