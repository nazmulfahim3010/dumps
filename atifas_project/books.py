# books.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from db_config import get_connection

BG = "#FADADD"
BTN = "#FF69B4"
TEXT = "#222222"

class BooksWindow:
    def __init__(self, master):
        self.win = tk.Toplevel(master)
        self.win.title("Manage Books")
        self.win.geometry("800x550")
        self.win.configure(bg=BG)

        tk.Label(self.win, text="Manage Books", bg=BG, fg=TEXT, font=Font(size=14, weight="bold")).pack(pady=8)
        form = tk.Frame(self.win, bg=BG)
        form.pack(pady=6)

        tk.Label(form, text="Title:", bg=BG).grid(row=0, column=0, sticky="e", padx=4, pady=6)
        self.title_e = tk.Entry(form, width=30)
        self.title_e.grid(row=0, column=1, padx=4, pady=6)

        tk.Label(form, text="Author:", bg=BG).grid(row=0, column=2, sticky="e", padx=4, pady=6)
        self.author_e = tk.Entry(form, width=25)
        self.author_e.grid(row=0, column=3, padx=4, pady=6)

        tk.Label(form, text="Category:", bg=BG).grid(row=1, column=0, sticky="e", padx=4, pady=6)
        self.category_e = tk.Entry(form, width=30)
        self.category_e.grid(row=1, column=1, padx=4, pady=6)

        tk.Label(form, text="Quantity:", bg=BG).grid(row=1, column=2, sticky="e", padx=4, pady=6)
        self.quantity_e = tk.Entry(form, width=10)
        self.quantity_e.grid(row=1, column=3, padx=4, pady=6)

        btn_frame = tk.Frame(self.win, bg=BG)
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Add Book", bg=BTN, fg="white", command=self.add_book).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update Book", bg=BTN, fg="white", command=self.update_book).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete Book", bg=BTN, fg="white", command=self.delete_book).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear", bg=BTN, fg="white", command=self.clear_fields).grid(row=0, column=3, padx=5)

        # search
        search_frame = tk.Frame(self.win, bg=BG)
        search_frame.pack(pady=6, fill="x")
        tk.Label(search_frame, text="Search (title/author):", bg=BG).pack(side="left", padx=6)
        self.search_e = tk.Entry(search_frame)
        self.search_e.pack(side="left", padx=6)
        tk.Button(search_frame, text="Search", bg=BTN, fg="white", command=self.search_books).pack(side="left", padx=4)
        tk.Button(search_frame, text="Show All", bg=BTN, fg="white", command=self.load_books).pack(side="left", padx=4)

        # treeview
        cols = ("ID","Title","Author","Category","Quantity")
        self.tree = ttk.Treeview(self.win, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=140, anchor="center")
        self.tree.pack(padx=10, pady=8, fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load_books()

    def execute(self, query, params=None, fetch=False):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(query, params or ())
            if fetch:
                rows = cur.fetchall()
                cur.close()
                conn.close()
                return rows
            cur.close()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            return None

    def add_book(self):
        title = self.title_e.get().strip()
        author = self.author_e.get().strip()
        category = self.category_e.get().strip()
        qty = self.quantity_e.get().strip()
        if not title or not author or not qty:
            messagebox.showerror("Validation", "Title, Author and Quantity are required")
            return
        try:
            qty_i = int(qty)
            if qty_i < 0:
                raise ValueError()
        except:
            messagebox.showerror("Validation", "Quantity must be a non-negative integer")
            return
        q = "INSERT INTO books (title, author, category, quantity) VALUES (%s,%s,%s,%s)"
        res = self.execute(q, (title, author, category, qty_i))
        if res:
            messagebox.showinfo("Success", "Book added")
            self.load_books()
            self.clear_fields()

    def load_books(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = self.execute("SELECT book_id, title, author, category, quantity FROM books ORDER BY title", fetch=True)
        if rows:
            for row in rows:
                self.tree.insert("", "end", values=row)

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])['values']
        # book_id, title, author, category, quantity
        self.selected_id = vals[0]
        self.title_e.delete(0, "end"); self.title_e.insert(0, vals[1])
        self.author_e.delete(0, "end"); self.author_e.insert(0, vals[2])
        self.category_e.delete(0, "end"); self.category_e.insert(0, vals[3])
        self.quantity_e.delete(0, "end"); self.quantity_e.insert(0, vals[4])

    def clear_fields(self):
        self.title_e.delete(0, 'end')
        self.author_e.delete(0, 'end')
        self.category_e.delete(0, 'end')
        self.quantity_e.delete(0, 'end')
        self.search_e.delete(0, 'end')
        self.selected_id = None

    def update_book(self):
        if not hasattr(self, 'selected_id') or not self.selected_id:
            messagebox.showerror("Select", "Select a book to update")
            return
        title = self.title_e.get().strip(); author = self.author_e.get().strip()
        category = self.category_e.get().strip(); qty = self.quantity_e.get().strip()
        if not title or not author or not qty:
            messagebox.showerror("Validation", "Title, Author and Quantity are required")
            return
        try:
            qty_i = int(qty); 
            if qty_i < 0: raise ValueError()
        except:
            messagebox.showerror("Validation", "Quantity must be a non-negative integer")
            return
        q = "UPDATE books SET title=%s, author=%s, category=%s, quantity=%s WHERE book_id=%s"
        res = self.execute(q, (title, author, category, qty_i, self.selected_id))
        if res:
            messagebox.showinfo("Success", "Book updated")
            self.load_books()
            self.clear_fields()

    def delete_book(self):
        if not hasattr(self, 'selected_id') or not self.selected_id:
            messagebox.showerror("Select", "Select a book to delete")
            return
        if not messagebox.askyesno("Confirm", "Delete selected book?"):
            return
        q = "DELETE FROM books WHERE book_id=%s"
        res = self.execute(q, (self.selected_id,))
        if res:
            messagebox.showinfo("Success", "Book deleted")
            self.load_books()
            self.clear_fields()

    def search_books(self):
        term = self.search_e.get().strip()
        if not term:
            messagebox.showerror("Input", "Enter search term")
            return
        query = "SELECT book_id, title, author, category, quantity FROM books WHERE title LIKE %s OR author LIKE %s ORDER BY title"
        rows = self.execute(query, (f"%{term}%", f"%{term}%"), fetch=True)
        for r in self.tree.get_children():
            self.tree.delete(r)
        if rows:
            for row in rows:
                self.tree.insert("", "end", values=row)
