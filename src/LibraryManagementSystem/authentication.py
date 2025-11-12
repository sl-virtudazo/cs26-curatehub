import tkinter as tk
from tkinter import messagebox
import re
from configuration import COLORS, FONTS


class AuthPage:
    def __init__(self, root, db, on_success):
        self.username_entry = None
        self.password_entry = None
        self.root = root
        self.db = db
        self.on_success = on_success
        self.frame = None

    def show(self):
        """Display authentication page"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main frame
        self.frame = tk.Frame(self.root, bg=COLORS['background'])
        self.frame.pack(fill='both', expand=True)

        # Center container
        center_frame = tk.Frame(self.frame, bg=COLORS['background'])
        center_frame.place(relx=0.5, rely=0.5, anchor='center')

        # ===== Title Section =====
        main_title = tk.Label(
            center_frame,
            text="CurateHub",
            font=FONTS['title'],
            bg=COLORS['background'],
            fg=COLORS['primary']
        )
        main_title.pack(pady=(0, 5))

        subtext = tk.Label(
            center_frame,
            text="A Library Management System",
            font=FONTS['small'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        subtext.pack(pady=(0, 25))

        # ===== Rounded Login Frame =====
        radius_px = 20
        canvas = tk.Canvas(center_frame, width=420, height=420, bg=COLORS['background'], highlightthickness=0)
        canvas.pack()

        # Draw rounded rectangle
        x1, y1, x2, y2 = 10, 10, 410, 410
        canvas.create_rectangle(x1 + radius_px, y1, x2 - radius_px, y2, fill="white", outline="")
        canvas.create_rectangle(x1, y1 + radius_px, x2, y2 - radius_px, fill="white", outline="")
        canvas.create_oval(x1, y1, x1 + 2 * radius_px, y1 + 2 * radius_px, fill="white", outline="")
        canvas.create_oval(x2 - 2 * radius_px, y1, x2, y1 + 2 * radius_px, fill="white", outline="")
        canvas.create_oval(x1, y2 - 2 * radius_px, x1 + 2 * radius_px, y2, fill="white", outline="")
        canvas.create_oval(x2 - 2 * radius_px, y2 - 2 * radius_px, x2, y2, fill="white", outline="")

        # Place login_frame inside canvas
        login_frame = tk.Frame(canvas, bg='white')
        canvas.create_window(210, 210, window=login_frame)

        # ===== Login Header =====
        login_header = tk.Label(
            login_frame,
            text="Welcome! Sign in to manage collections and discover new trends!",
            font=FONTS['small'],
            bg='white',
            fg=COLORS['text'],
            wraplength=320,
            justify='center'
        )
        login_header.pack(pady=20)

        # ===== Username Field =====
        username_label = tk.Label(
            login_frame,
            text="Username",
            font=FONTS['small'],
            bg='white',
            fg=COLORS['text']
        )
        username_label.pack(anchor='w', padx=30)

        self.username_entry = tk.Entry(
            login_frame,
            font=FONTS['small'],
            width=30
        )
        self.username_entry.pack(padx=30, pady=(0, 15))

        # ===== Password Field =====
        password_label = tk.Label(
            login_frame,
            text="Password",
            font=FONTS['small'],
            bg='white',
            fg=COLORS['text']
        )
        password_label.pack(anchor='w', padx=30)

        self.password_entry = tk.Entry(
            login_frame,
            font=FONTS['small'],
            width=30,
            show='*'
        )
        self.password_entry.pack(padx=30, pady=(0, 10))

        # Bind Enter key to log in
        self.username_entry.bind('<Return>', lambda e: self.login())
        self.password_entry.bind('<Return>', lambda e: self.login())

        # ===== Forgot Password Link =====
        forgot_btn = tk.Button(
            login_frame,
            text="Forgot Password?",
            font=FONTS['pass'],
            bg='white',
            fg=COLORS['primary'],
            bd=0,
            cursor='hand2',
            command=self.forgot_password
        )
        forgot_btn.pack(pady=(0, 15))

        # ===== Login Button =====
        login_btn = tk.Button(
            login_frame,
            text="Login",
            font=FONTS['login'],
            bg=COLORS['primary'],
            fg='white',
            width=20,
            cursor='hand2',
            command=self.login
        )
        login_btn.pack(pady=(10, 30), padx=30)

        # Hover effect for login button
        login_btn.bind('<Enter>', lambda e: login_btn.configure(bg=COLORS['secondary']))
        login_btn.bind('<Leave>', lambda e: login_btn.configure(bg=COLORS['primary']))

    def login(self):
        """Validate username and password"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        username_pattern = r'^[A-Za-z0-9_.]{1,50}(?<!\.)$'
        if not re.match(username_pattern, username):
            messagebox.showerror(
                "Error",
                "Username can only contain letters, numbers, underscores, and periods. "
                "It cannot end with a period and must be up to 50 characters.")
            return

        # Success
        messagebox.showinfo("Success", f"Welcome, {username}!")
        self.on_success()

    def forgot_password(self):
        """Handle forgot password functionality"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Forgot Password")
        dialog.geometry("400x250")
        dialog.configure(bg='white')
        dialog.resizable(False, False)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f'400x250+{x}+{y}')

        # Title
        tk.Label(
            dialog,
            text="Reset Password",
            font=FONTS['heading'],
            bg='white',
            fg=COLORS['text']
        ).pack(pady=20)

        # Instructions
        tk.Label(
            dialog,
            text="Enter your email address to receive\npassword reset instructions",
            font=FONTS['small'],
            bg='white',
            fg=COLORS['secondary'],
            justify='center'
        ).pack(pady=10)

        # Email field
        tk.Label(
            dialog,
            text="Email Address",
            font=FONTS['small'],
            bg='white',
            fg=COLORS['text']
        ).pack(anchor='w', padx=50)

        email_entry = tk.Entry(dialog, font=FONTS['small'], width=30)
        email_entry.pack(padx=50, pady=(0, 20))

        # Button frame
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(pady=10)

        def send_reset():
            email = email_entry.get().strip()

            if not email:
                messagebox.showerror("Error", "Please enter your email address", parent=dialog)
                return

            # Basic email validation
            email_pattern = r'^[^@]+@[^@]+\.[^@]+$'
            if not re.match(email_pattern, email, re.IGNORECASE):
                messagebox.showerror("Error", "Please enter a valid email address", parent=dialog)
                return

            # Success
            messagebox.showinfo(
                "Request Sent",
                f"Password reset instructions have been sent to:\n{email}\n\n"
                f"Please check your inbox and follow the instructions to reset your password.",
                parent=dialog
            )
            dialog.destroy()

        # Send button
        send_btn = tk.Button(
            btn_frame,
            text="Send Reset Link",
            font=FONTS['small'],
            bg=COLORS['primary'],
            fg='white',
            width=15,
            cursor='hand2',
            command=send_reset
        )
        send_btn.pack(side='left', padx=5)

        send_btn.bind('<Enter>', lambda e: send_btn.configure(bg=COLORS['secondary']))
        send_btn.bind('<Leave>', lambda e: send_btn.configure(bg=COLORS['primary']))

        # Cancel button
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=FONTS['small'],
            bg=COLORS['accent'],
            fg='white',
            width=15,
            cursor='hand2',
            command=dialog.destroy
        )
        cancel_btn.pack(side='left', padx=5)

        cancel_btn.bind('<Enter>', lambda e: cancel_btn.configure(bg=COLORS['secondary']))
        cancel_btn.bind('<Leave>', lambda e: cancel_btn.configure(bg=COLORS['accent']))
