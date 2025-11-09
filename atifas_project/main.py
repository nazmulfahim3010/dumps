# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from books import BooksWindow
from members import MembersWindow
from issue_return import IssueReturnWindow
from db_config import get_connection
import datetime

# Theme colors
BG = "#FADADD"  # light pink background
BTN = "#FF69B4"  # deep pink buttons
TEXT = "#222222"

class LoginWindow:
    def __init__(self, root):
        self.root = root
        root.title("Library Management System - Login")
        root.geometry("420x300")
        root.configure(bg=BG)
        root.resizable(False, False)

        self.title_font = Font(size=16, weight="bold")
        self.label_font = Font(size=11)
        self.entry_font = Font(size=11)

        tk.Label(root, text="Library Management System", bg=BG, fg=TEXT, font=self.title_font).pack(pady=15)
        frame = tk.Frame(root, bg=BG)
        frame.pack(pady=10)

        tk.Label(frame, text="Username:", bg=BG, fg=TEXT, font=self.label_font).grid(row=0, column=0, sticky="e", padx=5, pady=8)
        self.username = tk.Entry(frame, font=self.entry_font)
        self.username.grid(row=0, column=1, padx=5, pady=8)

        tk.Label(frame, text="Password:", bg=BG, fg=TEXT, font=self.label_font).grid(row=1, column=0, sticky="e", padx=5, pady=8)
        self.password = tk.Entry(frame, show="*", font=self.entry_font)
        self.password.grid(row=1, column=1, padx=5, pady=8)

        login_btn = tk.Button(root, text="Login", bg=BTN, fg="white", font=self.label_font, command=self.login)
        login_btn.pack(pady=12, ipadx=10, ipady=5)

        tk.Label(root, text="(Use admin / admin123 from sample data)", bg=BG, fg=TEXT, font=("Arial",9)).pack(side="bottom", pady=6)

    def login(self):
        user = self.username.get().strip()
        pwd = self.password.get().strip()
        if not user or not pwd:
            messagebox.showerror("Error", "Please enter username and password")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM admin WHERE username=%s", (user,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row and row[0] == pwd:
                self.root.destroy()
                DashboardWindow()
            else:
                messagebox.showerror("Login failed", "Invalid username or password")
        except Exception as e:
            messagebox.showerror("Database error", str(e))

class DashboardWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Library Dashboard")
        self.root.geometry("900x600")
        self.root.configure(bg=BG)

        self.title_font = Font(size=16, weight="bold")
        tk.Label(self.root, text="Library Dashboard", bg=BG, fg=TEXT, font=self.title_font).pack(pady=12)

        # Top buttons
        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(pady=8)

        b_books = tk.Button(btn_frame, text="Manage Books", bg=BTN, fg="white", command=self.open_books, width=16)
        b_books.grid(row=0, column=0, padx=8, pady=6)

        b_members = tk.Button(btn_frame, text="Manage Members", bg=BTN, fg="white", command=self.open_members, width=16)
        b_members.grid(row=0, column=1, padx=8, pady=6)

        b_issue = tk.Button(btn_frame, text="Issue / Return", bg=BTN, fg="white", command=self.open_issue_return, width=16)
        b_issue.grid(row=0, column=2, padx=8, pady=6)

        b_refresh = tk.Button(btn_frame, text="Refresh Stats", bg=BTN, fg="white", command=self.load_stats, width=16)
        b_refresh.grid(row=0, column=3, padx=8, pady=6)

        # Statistics frame
        stats_frame = tk.Frame(self.root, bg=BG)
        stats_frame.pack(pady=10, fill="x")

        self.stat_vars = {
            'books': tk.StringVar(value="0"),
            'members': tk.StringVar(value="0"),
            'issued': tk.StringVar(value="0"),
            'returned': tk.StringVar(value="0"),
            'overdue': tk.StringVar(value="0")
        }

        # neat labels
        for i, (k, var) in enumerate(self.stat_vars.items()):
            f = tk.Frame(stats_frame, bg=BG, bd=1, relief="groove")
            f.grid(row=0, column=i, padx=10, ipadx=10, ipady=12)
            tk.Label(f, text=k.capitalize(), bg=BG, fg=TEXT).pack()
            tk.Label(f, textvariable=var, bg=BG, fg=TEXT, font=Font(size=14, weight="bold")).pack()

        # Recent issued books tree
        tree_frame = tk.Frame(self.root, bg=BG)
        tree_frame.pack(pady=12, fill="both", expand=True)

        tk.Label(tree_frame, text="Recently Issued (Top 20)", bg=BG, fg=TEXT, font=Font(size=12)).pack(anchor="w", padx=10)

        cols = ("Issue ID","Book Title","Member","Issue Date","Due Date","Return Date","Status")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110, anchor="center")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10,0))
        vsb.pack(side="left", fill="y", padx=(0,10))

        self.load_stats()
        self.load_recent_issued()

        # bottom logout
        bottom = tk.Frame(self.root, bg=BG)
        bottom.pack(side="bottom", pady=8)
        tk.Button(bottom, text="Logout", bg=BTN, fg="white", command=self.logout).pack(ipadx=6, ipady=3)

        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)
        self.root.mainloop()

    def open_books(self):
        BooksWindow(self.root)

    def open_members(self):
        MembersWindow(self.root)

    def open_issue_return(self):
        IssueReturnWindow(self.root)

    def logout(self):
        if messagebox.askyesno("Confirm", "Logout and return to login?"):
            self.root.destroy()
            root = tk.Tk()
            LoginWindow(root)
            root.mainloop()

    def load_stats(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM books")
            books = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM members")
            members = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM issued_books WHERE status='issued'")
            issued = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM issued_books WHERE status='returned'")
            returned = cur.fetchone()[0]
            # overdue: issued & due_date < today
            cur.execute("SELECT COUNT(*) FROM issued_books WHERE status='issued' AND due_date < CURDATE()")
            overdue = cur.fetchone()[0]
            cur.close()
            conn.close()
            self.stat_vars['books'].set(str(books))
            self.stat_vars['members'].set(str(members))
            self.stat_vars['issued'].set(str(issued))
            self.stat_vars['returned'].set(str(returned))
            self.stat_vars['overdue'].set(str(overdue))
            self.load_recent_issued()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_recent_issued(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        try:
            conn = get_connection()
            cur = conn.cursor()
            query = """
                SELECT i.issue_id, b.title, m.name, i.issue_date, i.due_date, i.return_date, i.status
                FROM issued_books i
                JOIN books b ON i.book_id=b.book_id
                JOIN members m ON i.member_id=m.member_id
                ORDER BY i.issue_date DESC
                LIMIT 20
            """
            cur.execute(query)
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))
