# catalog_management.py

import tkinter as tk
from tkinter import ttk, messagebox
from configuration import COLORS, FONTS
from utilities import generate_id, validate_isbn
from datetime import datetime

class BookManagement:
    def __init__(self, parent, db):
        self.context_menu = None
        self.parent = parent
        self.db = db
        self.tree = None
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="All")
        self.status_var = tk.StringVar(value="All")

    def show(self):
        # Display book management interface
        # Header
        header = tk.Frame(self.parent, bg=COLORS['background'])
        header.pack(fill='x', padx=20, pady=20)

        title = tk.Label(
            header,
            text="Catalog Management",
            font=FONTS['heading'],
            bg=COLORS['background'],
            fg=COLORS['text'])
        title.pack(anchor='w')

        subtitle = tk.Label(
            header,
            text="Organize, update, and track all books in the library collection",
            font=FONTS['small'],
            bg=COLORS['background'],
            fg=COLORS['text'])
        subtitle.pack(anchor='w')

        # Search and filter frame
        search_frame = tk.Frame(self.parent, bg=COLORS['background'])
        search_frame.pack(fill='x', padx=20, pady=(0, 10))

        # Search bar
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=FONTS['small'],
            width=40)
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self.search_books())

        search_btn = tk.Button(
            search_frame,
            text="Search",
            font=FONTS['small'],
            bg=COLORS['primary'],
            fg='white',
            cursor='hand2',
            command=self.search_books)
        search_btn.pack(side='left', padx=(0, 20))

        # Hover effect
        search_btn.bind('<Enter>', lambda e: search_btn.configure(bg=COLORS['secondary']))
        search_btn.bind('<Leave>', lambda e: search_btn.configure(bg=COLORS['primary']))

        # Category dropdown
        (tk.Label(
            search_frame,
            text="Category:",
            font=FONTS['small'],
            bg=COLORS['background'],
            fg=COLORS['text']).
         pack(side='left'))

        # 15 book categories in alphabetical order
        categories = [
            "Adventure", "Art", "Biography", "Business", "Cooking",
            "Fantasy", "Fiction", "History", "Horror", "Mystery",
            "Non-Fiction", "Poetry", "Romance", "Science", "Technology"]
        categories.insert(0, "All")

        category_combo = ttk.Combobox(
            search_frame,
            textvariable=self.category_var,
            values=categories,
            state='readonly',
            width=18)
        category_combo.pack(side='left', padx=5)
        category_combo.bind('<<ComboboxSelected>>', lambda e: self.load_books())

        # Status dropdown
        (tk.Label(
            search_frame,
            text="Status:",
            font=FONTS['small'],
            bg=COLORS['background'],
            fg=COLORS['text']).
         pack(side='left', padx=(10, 0)))

        statuses = ["All", "Available", "Borrowed"]
        status_combo = ttk.Combobox(
            search_frame,
            textvariable=self.status_var,
            values=statuses,
            state='readonly',
            width=15)
        status_combo.pack(side='left', padx=5)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.load_books())

        # Add new book button
        add_btn = tk.Button(
            search_frame,
            text="+ Add New Book",
            font=FONTS['small'],
            bg=COLORS['accent'],
            fg='white',
            cursor='hand2',
            command=self.add_book_dialog)
        add_btn.pack(side='right')

        # Hover effect
        add_btn.bind('<Enter>', lambda e: add_btn.configure(bg=COLORS['secondary']))
        add_btn.bind('<Leave>', lambda e: add_btn.configure(bg=COLORS['accent']))

        # Table frame with scrollbar
        table_frame = tk.Frame(self.parent, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side='right', fill='y')

        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')

        # Treeview (table)
        columns = ('book_id', 'title', 'author', 'isbn', 'category', 'status', 'added_at', 'updated_at')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set)

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Define headings
        for col, text in zip(columns,['Book ID', 'Title', 'Author', 'ISBN', 'Category', 'Status', 'Added At', 'Updated At']):
            self.tree.heading(col, text=text)

        # Define column widths
        self.tree.column('book_id', width=100)
        self.tree.column('title', width=250)
        self.tree.column('author', width=200)
        self.tree.column('isbn', width=150)
        self.tree.column('category', width=120)
        self.tree.column('status', width=100)
        self.tree.column('added_at', width=150)
        self.tree.column('updated_at', width=150)

        self.tree.pack(fill='both', expand=True)

        # Right-click menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="View Details", command=self.view_book_details)
        self.context_menu.add_command(label="Update Details", command=self.update_book_dialog)
        self.context_menu.add_command(label="Delete Book", command=self.delete_book)

        self.tree.bind('<Button-3>', self.show_context_menu)

        # Load initial data
        self.load_books()

    def show_context_menu(self, event):
        # Show right-click context menu
        try:
            self.tree.selection_set(self.tree.identify_row(event.y))
            self.context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Context menu error: {e}")

    def load_books(self):
        # Load books from database with category and status filters
        for item in self.tree.get_children():
            self.tree.delete(item)

        category_filter = self.category_var.get()
        status_filter = self.status_var.get()

        # Base query
        query = "SELECT * FROM books"
        params = []

        # Apply filters
        conditions = []
        if category_filter != "All":
            conditions.append("category = %s")
            params.append(category_filter)

        if status_filter != "All":
            conditions.append("status = %s")
            params.append(status_filter)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY book_id"  # Preserve book ID order
        books = self.db.fetch_all(query, tuple(params))

        for book in books:
            self.tree.insert('', 'end', values=(
                book['book_id'],
                book['title'],
                book['author'],
                book['isbn'],
                book['category'],
                book['status'],
                book['added_at'].strftime("%Y-%m-%d %H:%M:%S") if book['added_at'] else "",
                book['updated_at'].strftime("%Y-%m-%d %H:%M:%S") if book['updated_at'] else ""))

    def search_books(self):
        # Search books by keyword
        keyword = self.search_var.get().strip()

        if not keyword:
            self.load_books()
            return
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
        SELECT * FROM books 
        WHERE book_id LIKE %s OR title LIKE %s OR author LIKE %s OR isbn LIKE %s
        ORDER BY book_id
        """
        search_pattern = f"%{keyword}%"
        books = self.db.fetch_all(query, (search_pattern,) * 4)

        for book in books:
            self.tree.insert('', 'end', values=(
                book['book_id'],
                book['title'],
                book['author'],
                book['isbn'],
                book['category'],
                book['status'],
                book['added_at'].strftime("%Y-%m-%d %H:%M:%S") if book['added_at'] else "",
                book['updated_at'].strftime("%Y-%m-%d %H:%M:%S") if book['updated_at'] else ""))

    def view_book_details(self):
        # Show book details in a dialog
        selected = self.tree.selection()
        if not selected:
            return

        book_id = self.tree.item(selected[0])['values'][0]
        book = self.db.fetch_one("SELECT * FROM books WHERE book_id = %s", (book_id,))

        if not book:
            return

        dialog = tk.Toplevel(self.parent)
        dialog.title("Book Details")
        dialog.geometry("500x400")
        dialog.configure(bg='white')
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f'500x400+{x}+{y}')

        tk.Label(dialog, text="Book Details", font=FONTS['heading'], bg='white', fg=COLORS['text']).pack(pady=15)

        details_frame = tk.Frame(dialog, bg='white')
        details_frame.pack(padx=30, pady=10, fill='both', expand=True)

        # Book details
        details = [
            ("Book ID:", book['book_id']),
            ("Title:", book['title']),
            ("Author:", book['author']),
            ("ISBN:", book['isbn']),
            ("Category:", book['category']),
            ("Status:", book['status']),
            ("Added At:", book['added_at'].strftime("%Y-%m-%d %H:%M:%S") if book['added_at'] else ""),
            ("Updated At:", book['updated_at'].strftime("%Y-%m-%d %H:%M:%S") if book['updated_at'] else "")]

        for label, value in details:
            row = tk.Frame(details_frame, bg='white')
            row.pack(fill='x', pady=2)

            (tk.Label(
                row,
                text=label,
                font=FONTS['small'],
                bg='white',
                fg=COLORS['text'],
                width=15,
                anchor='w').
             pack(side='left'))

            (tk.Label(
                row,
                text=value,
                font=FONTS['small'],
                bg='white',
                fg=COLORS['text'],
                anchor='w').
             pack(side='left', fill='x', expand=True))

        close_btn = tk.Button(
            dialog,
            text="Close",
            font=FONTS['small'],
            bg=COLORS['primary'],
            fg='white',
            width=10,
            command=dialog.destroy)
        close_btn.pack(pady=10)

        # Hover effect
        close_btn.bind('<Enter>', lambda e: close_btn.configure(bg=COLORS['secondary']))
        close_btn.bind('<Leave>', lambda e: close_btn.configure(bg=COLORS['primary']))

    def add_book_dialog(self):
        # Show add book dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Book")
        dialog.geometry("500x450")
        dialog.configure(bg='white')
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (450 // 2)
        dialog.geometry(f'500x450+{x}+{y}')

        tk.Label(dialog, text="Add New Book", font=FONTS['heading'], bg='white', fg=COLORS['text']).pack(pady=20)
        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(padx=30, fill='both', expand=True)

        tk.Label(form_frame, text="Title*", font=FONTS['small'], bg='white').pack(anchor='w')
        title_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        title_entry.pack(pady=(0, 15))

        tk.Label(form_frame, text="Author*", font=FONTS['small'], bg='white').pack(anchor='w')
        author_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        author_entry.pack(pady=(0, 15))

        tk.Label(form_frame, text="ISBN*", font=FONTS['small'], bg='white').pack(anchor='w')
        isbn_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        isbn_entry.pack(pady=(0, 15))

        tk.Label(form_frame, text="Category*", font=FONTS['small'], bg='white').pack(anchor='w')

        # 15 categories in alphabetical order
        categories = [
            "Adventure", "Art", "Biography", "Business", "Cooking",
            "Fantasy", "Fiction", "History", "Horror", "Mystery",
            "Non-Fiction", "Poetry", "Romance", "Science", "Technology"]

        category_combo = ttk.Combobox(form_frame, values=categories, state='readonly', width=37)
        category_combo.pack(pady=(0, 20))
        category_combo.set("Fiction")

        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(pady=20)

        def save_book():
            title = title_entry.get().strip()
            author = author_entry.get().strip()
            isbn = isbn_entry.get().strip()
            category = category_combo.get()

            if not all([title, author, isbn, category]):
                messagebox.showerror("Error", "All fields are required", parent=dialog)
                return
            if not validate_isbn(isbn):
                messagebox.showerror("Error", "Invalid ISBN format", parent=dialog)
                return

            last_book = self.db.fetch_one("SELECT book_id FROM books ORDER BY book_id DESC LIMIT 1")
            book_id = generate_id("BK", last_book['book_id'] if last_book else None)
            now = datetime.now()

            query = """
            INSERT INTO books (book_id, title, author, isbn, category, status, added_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, 'Available', %s, %s)
            """

            if self.db.execute_query(query, (book_id, title, author, isbn, category, now, now)):
                messagebox.showinfo("Success", f"Book added successfully! (ID: {book_id})", parent=dialog)
                dialog.destroy()
                self.load_books()
            else:
                messagebox.showerror("Error", "Failed to add book", parent=dialog)

        save_btn = tk.Button(btn_frame, text="Save Book", font=FONTS['small'], bg=COLORS['primary'],
                             fg='white', width=15, cursor='hand2', command=save_book)
        save_btn.pack(side='left', padx=5)
        save_btn.bind('<Enter>', lambda e: save_btn.configure(bg=COLORS['secondary']))
        save_btn.bind('<Leave>', lambda e: save_btn.configure(bg=COLORS['primary']))

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=FONTS['small'], bg=COLORS['accent'],
                               fg='white', width=15, cursor='hand2', command=dialog.destroy)
        cancel_btn.pack(side='left', padx=5)
        cancel_btn.bind('<Enter>', lambda e: cancel_btn.configure(bg=COLORS['secondary']))
        cancel_btn.bind('<Leave>', lambda e: cancel_btn.configure(bg=COLORS['accent']))

    def update_book_dialog(self):
        # Show update book dialog
        selected = self.tree.selection()
        if not selected:
            return

        book_id = self.tree.item(selected[0])['values'][0]
        book = self.db.fetch_one("SELECT * FROM books WHERE book_id = %s", (book_id,))

        if not book:
            return

        dialog = tk.Toplevel(self.parent)
        dialog.title("Update Book")
        dialog.geometry("500x450")
        dialog.configure(bg='white')
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (450 // 2)
        dialog.geometry(f'500x450+{x}+{y}')

        tk.Label(dialog, text="Update Book", font=FONTS['heading'], bg='white', fg=COLORS['text']).pack(pady=20)
        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(padx=30, fill='both', expand=True)

        tk.Label(form_frame, text="Title*", font=FONTS['small'], bg='white').pack(anchor='w')
        title_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        title_entry.insert(0, book['title'])
        title_entry.pack(pady=(0, 15))

        tk.Label(form_frame, text="Author*", font=FONTS['small'], bg='white').pack(anchor='w')
        author_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        author_entry.insert(0, book['author'])
        author_entry.pack(pady=(0, 15))

        tk.Label(form_frame, text="ISBN*", font=FONTS['small'], bg='white').pack(anchor='w')
        isbn_entry = tk.Entry(form_frame, font=FONTS['small'], width=40)
        isbn_entry.insert(0, book['isbn'])
        isbn_entry.pack(pady=(0, 15))

        tk.Label(form_frame, text="Category*", font=FONTS['small'], bg='white').pack(anchor='w')

        # 15 categories in alphabetical order
        categories = [
            "Adventure", "Art", "Biography", "Business", "Cooking",
            "Fantasy", "Fiction", "History", "Horror", "Mystery",
            "Non-Fiction", "Poetry", "Romance", "Science", "Technology"]

        category_combo = ttk.Combobox(form_frame, values=categories, state='readonly', width=37)
        category_combo.set(book['category'])
        category_combo.pack(pady=(0, 20))

        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(pady=20)

        def update_book():
            title = title_entry.get().strip()
            author = author_entry.get().strip()
            isbn = isbn_entry.get().strip()
            category = category_combo.get()

            if not all([title, author, isbn, category]):
                messagebox.showerror("Error", "All fields are required", parent=dialog)
                return

            now = datetime.now()

            query = """
            UPDATE books 
            SET title = %s, author = %s, isbn = %s, category = %s, updated_at = %s
            WHERE book_id = %s
            """

            if self.db.execute_query(query, (title, author, isbn, category, now, book_id)):
                messagebox.showinfo("Success", "Book updated successfully!", parent=dialog)
                dialog.destroy()
                self.load_books()
            else:
                messagebox.showerror("Error", "Failed to update book", parent=dialog)

        update_btn = tk.Button(btn_frame, text="Update Book", font=FONTS['small'], bg=COLORS['primary'],
                               fg='white', width=15, cursor='hand2', command=update_book)
        update_btn.pack(side='left', padx=5)
        update_btn.bind('<Enter>', lambda e: update_btn.configure(bg=COLORS['secondary']))
        update_btn.bind('<Leave>', lambda e: update_btn.configure(bg=COLORS['primary']))

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=FONTS['small'], bg=COLORS['accent'],
                               fg='white', width=15, cursor='hand2', command=dialog.destroy)
        cancel_btn.pack(side='left', padx=5)
        cancel_btn.bind('<Enter>', lambda e: cancel_btn.configure(bg=COLORS['secondary']))
        cancel_btn.bind('<Leave>', lambda e: cancel_btn.configure(bg=COLORS['accent']))

    def delete_book(self):
        # Delete book with confirmation
        selected = self.tree.selection()
        if not selected:
            return

        book_id = self.tree.item(selected[0])['values'][0]
        book_title = self.tree.item(selected[0])['values'][1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{book_title}'?"):
            query = "DELETE FROM books WHERE book_id = %s"
            if self.db.execute_query(query, (book_id,)):
                messagebox.showinfo("Success", "Book deleted successfully!")
                self.load_books()
            else:
                messagebox.showerror("Error", "Failed to delete book")