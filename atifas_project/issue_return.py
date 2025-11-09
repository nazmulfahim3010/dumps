# issue_return.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from db_config import get_connection
import datetime

BG = "#FADADD"
BTN = "#FF69B4"
TEXT = "#222222"

class IssueReturnWindow:
    def __init__(self, master):
        self.win = tk.Toplevel(master)
        self.win.title("Issue and Return Books")
        self.win.geometry("900x620")
        self.win.configure(bg=BG)

        tk.Label(self.win, text="Issue / Return Books", bg=BG, fg=TEXT, font=Font(size=14,weight="bold")).pack(pady=8)

        # Issue form
        form = tk.Frame(self.win, bg=BG)
        form.pack(pady=6, fill="x")

        tk.Label(form, text="Book ID:", bg=BG).grid(row=0,column=0,padx=4,sticky="e")
        self.book_id_e = tk.Entry(form, width=10); self.book_id_e.grid(row=0,column=1,padx=4)

        tk.Label(form, text="Member ID:", bg=BG).grid(row=0,column=2,padx=4,sticky="e")
        self.member_id_e = tk.Entry(form, width=10); self.member_id_e.grid(row=0,column=3,padx=4)

        tk.Label(form, text="Days (due after):", bg=BG).grid(row=0,column=4,padx=4,sticky="e")
        self.days_e = tk.Entry(form, width=8); self.days_e.grid(row=0,column=5,padx=4)
        self.days_e.insert(0, "14")

        tk.Button(form, text="Issue Book", bg=BTN, fg="white", command=self.issue_book).grid(row=0,column=6,padx=6)

        # Return form
        rframe = tk.Frame(self.win, bg=BG)
        rframe.pack(pady=6, fill="x")
        tk.Label(rframe, text="Issue ID to return:", bg=BG).grid(row=0,column=0,padx=4,sticky="e")
        self.return_id_e = tk.Entry(rframe, width=12); self.return_id_e.grid(row=0,column=1,padx=4)
        tk.Button(rframe, text="Return Book", bg=BTN, fg="white", command=self.return_book).grid(row=0,column=2,padx=6)

        # Search and overdue
        search_frame = tk.Frame(self.win, bg=BG)
        search_frame.pack(pady=6, fill="x")
        tk.Label(search_frame, text="Search (book title / member name):", bg=BG).pack(side="left", padx=6)
        self.search_e = tk.Entry(search_frame, width=30); self.search_e.pack(side="left", padx=6)
        tk.Button(search_frame, text="Search", bg=BTN, fg="white", command=self.search_issued).pack(side="left", padx=4)
        tk.Button(search_frame, text="Show All Issued", bg=BTN, fg="white", command=self.load_issued).pack(side="left", padx=4)
        tk.Button(search_frame, text="Show Overdue", bg=BTN, fg="white", command=self.load_overdue).pack(side="left", padx=4)

        # Treeview for issued records
        cols = ("Issue ID","Book ID","Book Title","Member ID","Member","Issue Date","Due Date","Return Date","Status")
        self.tree = ttk.Treeview(self.win, columns=cols, show="headings", height=18)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, anchor="center")
        self.tree.pack(padx=10, pady=8, fill="both", expand=True)
        self.load_issued()

    def execute(self, q, params=None, fetch=False):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(q, params or ())
            if fetch:
                rows = cur.fetchall()
                cur.close()
                conn.close()
                return rows
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            return None

    def issue_book(self):
        book_id = self.book_id_e.get().strip()
        member_id = self.member_id_e.get().strip()
        days = self.days_e.get().strip()
        if not book_id or not member_id or not days:
            messagebox.showerror("Validation", "All issue fields are required")
            return
        try:
            book_id_i = int(book_id); member_id_i = int(member_id); days_i = int(days)
        except:
            messagebox.showerror("Validation", "IDs and days must be integers")
            return
        # Check book available
        row = self.execute("SELECT quantity, title FROM books WHERE book_id=%s", (book_id_i,), fetch=True)
        if not row:
            messagebox.showerror("Error", "Book not found")
            return
        quantity, title = row[0][0], row[0][1]
        if quantity <= 0:
            messagebox.showerror("Unavailable", f"Book '{title}' is not available (quantity=0)")
            return
        # Check member exists
        row = self.execute("SELECT name FROM members WHERE member_id=%s", (member_id_i,), fetch=True)
        if not row:
            messagebox.showerror("Error", "Member not found")
            return
        issue_date = datetime.date.today()
        due_date = issue_date + datetime.timedelta(days=days_i)
        q1 = "INSERT INTO issued_books (book_id, member_id, issue_date, due_date, status) VALUES (%s,%s,%s,%s,'issued')"
        res = self.execute(q1, (book_id_i, member_id_i, issue_date, due_date))
        if res:
            # decrement book quantity
            self.execute("UPDATE books SET quantity = quantity - 1 WHERE book_id=%s", (book_id_i,))
            messagebox.showinfo("Success", "Book issued successfully")
            self.load_issued()
            self.clear_issue_fields()

    def clear_issue_fields(self):
        self.book_id_e.delete(0,'end'); self.member_id_e.delete(0,'end'); self.days_e.delete(0,'end')
        self.days_e.insert(0, "14")

    def return_book(self):
        issue_id = self.return_id_e.get().strip()
        if not issue_id:
            messagebox.showerror("Validation", "Enter issue ID")
            return
        try:
            issue_id_i = int(issue_id)
        except:
            messagebox.showerror("Validation", "Issue ID must be integer")
            return
        # Check issued record
        rows = self.execute("SELECT book_id, status FROM issued_books WHERE issue_id=%s", (issue_id_i,), fetch=True)
        if not rows:
            messagebox.showerror("Error", "Issue record not found")
            return
        book_id = rows[0][0]; status = rows[0][1]
        if status == 'returned':
            messagebox.showinfo("Info", "This book is already returned")
            return
        today = datetime.date.today()
        q = "UPDATE issued_books SET return_date=%s, status='returned' WHERE issue_id=%s"
        res = self.execute(q, (today, issue_id_i))
        if res:
            # increase book quantity
            self.execute("UPDATE books SET quantity = quantity + 1 WHERE book_id=%s", (book_id,))
            messagebox.showinfo("Success", "Book returned")
            self.load_issued()
            self.return_id_e.delete(0,'end')

    def load_issued(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        q = """
            SELECT i.issue_id, i.book_id, b.title, i.member_id, m.name, i.issue_date, i.due_date, i.return_date, i.status
            FROM issued_books i
            JOIN books b ON i.book_id=b.book_id
            JOIN members m ON i.member_id=m.member_id
            ORDER BY i.issue_date DESC
        """
        rows = self.execute(q, fetch=True)
        if rows:
            for row in rows:
                self.tree.insert("", "end", values=row)

    def load_overdue(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        q = """
            SELECT i.issue_id, i.book_id, b.title, i.member_id, m.name, i.issue_date, i.due_date, i.return_date, i.status
            FROM issued_books i
            JOIN books b ON i.book_id=b.book_id
            JOIN members m ON i.member_id=m.member_id
            WHERE i.status='issued' AND i.due_date < CURDATE()
            ORDER BY i.due_date ASC
        """
        rows = self.execute(q, fetch=True)
        if rows:
            for row in rows:
                self.tree.insert("", "end", values=row)
        else:
            messagebox.showinfo("Info", "No overdue records found")

    def search_issued(self):
        term = self.search_e.get().strip()
        if not term:
            messagebox.showerror("Input", "Enter search term")
            return
        for r in self.tree.get_children():
            self.tree.delete(r)
        q = """
            SELECT i.issue_id, i.book_id, b.title, i.member_id, m.name, i.issue_date, i.due_date, i.return_date, i.status
            FROM issued_books i
            JOIN books b ON i.book_id=b.book_id
            JOIN members m ON i.member_id=m.member_id
            WHERE b.title LIKE %s OR m.name LIKE %s
            ORDER BY i.issue_date DESC
        """
        rows = self.execute(q, (f"%{term}%", f"%{term}%"), fetch=True)
        if rows:
            for row in rows:
                self.tree.insert("", "end", values=row)
        else:
            messagebox.showinfo("Info", "No matching records")
