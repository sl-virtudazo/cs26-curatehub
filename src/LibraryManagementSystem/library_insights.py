# library_insights.py
# Reports and analytics dashboard (Fixed table labels and columns)

import tkinter as tk
from tkinter import ttk
from configuration import COLORS, FONTS
from utilities import format_currency


class ReportsAnalytics:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db

    def show(self):
        """Display reports and analytics interface"""
        # Header
        header = tk.Frame(self.parent, bg=COLORS['background'])
        header.pack(fill='x', padx=20, pady=20)

        title = tk.Label(
            header,
            text="Reports & Analytics",
            font=FONTS['heading'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        title.pack(anchor='w')

        subtitle = tk.Label(
            header,
            text="View library statistics, analyze borrowing trends, and track overall activity",
            font=FONTS['small'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        subtitle.pack(anchor='w')

        # Scrollable content frame
        canvas = tk.Canvas(self.parent, bg=COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['background'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")

        # Statistics Cards
        cards_frame = tk.Frame(scrollable_frame, bg=COLORS['background'])
        cards_frame.pack(fill='x', pady=20)

        # Get statistics
        stats = self.get_statistics()

        # Card 1: Total Members
        self.create_card(
            cards_frame,
            "Total Members",
            f"{stats['active_members']} active | {stats['inactive_members']} inactive",
            "patron account summary",
            0
        )

        # Card 2: Currently Borrowed Books
        self.create_card(
            cards_frame,
            "Currently Borrowed",
            f"{stats['borrowed_books']} {'book' if stats['borrowed_books'] <= 1 else 'books'}",
            "total items on loan",
            1
        )

        # Card 3: Overdue Books
        self.create_card(
            cards_frame,
            "Overdue Books",
            f"{stats['overdue_books']} {'book' if stats['overdue_books'] <= 1 else 'books'}",
            "follow-up required",
            2
        )

        # Card 4: Total Fines
        self.create_card(
            cards_frame,
            "Total Fines",
            format_currency(stats['total_fines']),
            "unpaid penalties",
            3
        )

        # Tables container
        tables_frame = tk.Frame(scrollable_frame, bg=COLORS['background'])
        tables_frame.pack(fill='both', expand=True, pady=20)

        # Table 1: Top Borrowers (Members with most borrowed books)
        self.create_top_borrowers_table(tables_frame)

        # Table 2: Most Popular Books
        self.create_popular_books_table(tables_frame)

    def get_statistics(self):
        """Get all statistics from database"""
        stats = {}

        # Active members
        result = self.db.fetch_one("SELECT COUNT(*) as count FROM members WHERE status = 'Active'")
        stats['active_members'] = result['count'] if result else 0

        # Inactive members
        result = self.db.fetch_one("SELECT COUNT(*) as count FROM members WHERE status = 'Inactive'")
        stats['inactive_members'] = result['count'] if result else 0

        # Currently borrowed books
        result = self.db.fetch_one("SELECT COUNT(*) as count FROM borrowed_books WHERE status = 'Borrowed'")
        stats['borrowed_books'] = result['count'] if result else 0

        # Overdue books
        result = self.db.fetch_one("SELECT COUNT(*) as count FROM borrowed_books WHERE status = 'Overdue'")
        stats['overdue_books'] = result['count'] if result else 0

        # Total fines
        result = self.db.fetch_one(
            "SELECT SUM(fine_amount) as total FROM borrowed_books WHERE status IN ('Overdue', 'Borrowed')"
        )
        stats['total_fines'] = result['total'] if result and result['total'] else 0

        return stats

    @staticmethod
    def create_card(parent, title, value, subtitle, column):
        """Create a statistics card"""
        card = tk.Frame(
            parent,
            bg='white',
            relief='solid',
            borderwidth=1
        )
        card.grid(row=0, column=column, padx=10, pady=10, sticky='ew')
        parent.grid_columnconfigure(column, weight=1)

        tk.Label(card, text=title, font=FONTS['small'], bg='white', fg=COLORS['text']).pack(pady=(15, 5))
        tk.Label(card, text=value, font=FONTS['heading'], bg='white', fg=COLORS['primary']).pack(pady=5)
        tk.Label(card, text=subtitle, font=FONTS['small'], bg='white', fg=COLORS['secondary']).pack(pady=(5, 15))

    def create_top_borrowers_table(self, parent):
        """Create top borrowers table - Members with the most borrowed books"""
        container = tk.Frame(parent, bg='white', relief='solid', borderwidth=1)
        container.pack(fill='both', expand=True, padx=10, pady=10)

        header_frame = tk.Frame(container, bg='white')
        header_frame.pack(fill='x', padx=20, pady=15)

        tk.Label(header_frame, text="Top Borrowers", font=FONTS['subheading'], bg='white', fg=COLORS['text']).pack(anchor='w')
        tk.Label(header_frame, text="Members with the most borrowed books", font=FONTS['small'], bg='white', fg=COLORS['secondary']).pack(anchor='w')

        table_frame = tk.Frame(container, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar.pack(side='right', fill='y')

        columns = ('rank', 'member', 'borrowed_books', 'total_fines')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=5, yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)

        tree.heading('rank', text='Rank')
        tree.heading('member', text='Member Name')
        tree.heading('borrowed_books', text='Borrowed Books')
        tree.heading('total_fines', text='Total Fines')

        tree.column('rank', width=80)
        tree.column('member', width=300)
        tree.column('borrowed_books', width=150)
        tree.column('total_fines', width=150)

        tree.pack(fill='both', expand=True)

        query = """
        SELECT 
            m.member_id,
            m.full_name,
            COUNT(bb.borrow_id) as total_borrowed,
            COALESCE(SUM(bb.fine_amount), 0) as total_fines
        FROM members m
        LEFT JOIN borrowed_books bb ON m.member_id = bb.member_id
        GROUP BY m.member_id, m.full_name
        HAVING total_borrowed > 0
        ORDER BY total_borrowed DESC
        LIMIT 10
        """
        borrowers = self.db.fetch_all(query)

        for idx, borrower in enumerate(borrowers, 1):
            tree.insert('', 'end', values=(
                f"#{idx}",
                f"{borrower['full_name']} – {borrower['member_id']}",
                f"{borrower['total_borrowed']} books",
                format_currency(borrower['total_fines'])
            ))

    def create_popular_books_table(self, parent):
        """Create most popular books table - Books borrowed most of the time"""
        container = tk.Frame(parent, bg='white', relief='solid', borderwidth=1)
        container.pack(fill='both', expand=True, padx=10, pady=10)

        header_frame = tk.Frame(container, bg='white')
        header_frame.pack(fill='x', padx=20, pady=15)

        tk.Label(header_frame, text="Most Popular Books", font=FONTS['subheading'], bg='white', fg=COLORS['text']).pack(anchor='w')
        tk.Label(header_frame, text="Books borrowed most of the time", font=FONTS['small'], bg='white', fg=COLORS['secondary']).pack(anchor='w')

        table_frame = tk.Frame(container, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar.pack(side='right', fill='y')

        columns = ('rank', 'book', 'times_borrowed')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=5, yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)

        tree.heading('rank', text='Rank')
        tree.heading('book', text='Book')
        tree.heading('times_borrowed', text='Times Borrowed')

        tree.column('rank', width=80)
        tree.column('book', width=450)
        tree.column('times_borrowed', width=150)

        tree.pack(fill='both', expand=True)

        query = """
        SELECT 
            b.book_id,
            b.title,
            b.author,
            COUNT(bb.borrow_id) as borrow_count
        FROM books b
        LEFT JOIN borrowed_books bb ON b.book_id = bb.book_id
        GROUP BY b.book_id, b.title, b.author
        HAVING borrow_count > 0
        ORDER BY borrow_count DESC
        LIMIT 10
        """
        books = self.db.fetch_all(query)

        for idx, book in enumerate(books, 1):
            tree.insert('', 'end', values=(
                f"#{idx}",
                f"{book['title']} – {book['author']}",
                f"{book['borrow_count']}x"
            ))
