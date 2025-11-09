# members.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from db_config import get_connection

BG = "#FADADD"
BTN = "#FF69B4"
TEXT = "#222222"

class MembersWindow:
    def __init__(self, master):
        self.win = tk.Toplevel(master)
        self.win.title("Manage Members")
        self.win.geometry("820x520")
        self.win.configure(bg=BG)

        tk.Label(self.win, text="Manage Members", bg=BG, fg=TEXT, font=Font(size=14,weight="bold")).pack(pady=8)

        form = tk.Frame(self.win, bg=BG)
        form.pack(pady=6)

        tk.Label(form, text="Name:", bg=BG).grid(row=0, column=0, sticky="e", padx=4, pady=6)
        self.name_e = tk.Entry(form, width=30); self.name_e.grid(row=0,column=1)

        tk.Label(form, text="Department:", bg=BG).grid(row=0, column=2, sticky="e", padx=4)
        self.dept_e = tk.Entry(form, width=20); self.dept_e.grid(row=0,column=3)

        tk.Label(form, text="Phone:", bg=BG).grid(row=1, column=0, sticky="e", padx=4, pady=6)
        self.phone_e = tk.Entry(form, width=20); self.phone_e.grid(row=1,column=1)

        tk.Label(form, text="Email:", bg=BG).grid(row=1, column=2, sticky="e", padx=4)
        self.email_e = tk.Entry(form, width=25); self.email_e.grid(row=1,column=3)

        btn_frame = tk.Frame(self.win, bg=BG)
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Add Member", bg=BTN, fg="white", command=self.add_member).grid(row=0,column=0,padx=5)
        tk.Button(btn_frame, text="Update Member", bg=BTN, fg="white", command=self.update_member).grid(row=0,column=1,padx=5)
        tk.Button(btn_frame, text="Delete Member", bg=BTN, fg="white", command=self.delete_member).grid(row=0,column=2,padx=5)
        tk.Button(btn_frame, text="Clear", bg=BTN, fg="white", command=self.clear_fields).grid(row=0,column=3,padx=5)

        search_frame = tk.Frame(self.win, bg=BG)
        search_frame.pack(pady=6, fill="x")
        tk.Label(search_frame, text="Search (name/email):", bg=BG).pack(side="left", padx=6)
        self.search_e = tk.Entry(search_frame); self.search_e.pack(side="left", padx=6)
        tk.Button(search_frame, text="Search", bg=BTN, fg="white", command=self.search_members).pack(side="left", padx=4)
        tk.Button(search_frame, text="Show All", bg=BTN, fg="white", command=self.load_members).pack(side="left", padx=4)

        cols = ("ID","Name","Department","Phone","Email")
        self.tree = ttk.Treeview(self.win, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=140, anchor="center")
        self.tree.pack(padx=10, pady=8, fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load_members()

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
            cur.close()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            return None

    def add_member(self):
        name = self.name_e.get().strip()
        dept = self.dept_e.get().strip()
        phone = self.phone_e.get().strip()
        email = self.email_e.get().strip()
        if not name:
            messagebox.showerror("Validation", "Name is required")
            return
        q = "INSERT INTO members (name, department, phone, email) VALUES (%s,%s,%s,%s)"
        res = self.execute(q, (name, dept, phone, email))
        if res:
            messagebox.showinfo("Success", "Member added")
            self.load_members()
            self.clear_fields()

    def load_members(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = self.execute("SELECT member_id, name, department, phone, email FROM members ORDER BY name", fetch=True)
        if rows:
            for row in rows:
                self.tree.insert("", "end", values=row)

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        self.selected_id = vals[0]
        self.name_e.delete(0,'end'); self.name_e.insert(0, vals[1])
        self.dept_e.delete(0,'end'); self.dept_e.insert(0, vals[2])
        self.phone_e.delete(0,'end'); self.phone_e.insert(0, vals[3])
        self.email_e.delete(0,'end'); self.email_e.insert(0, vals[4])

    def clear_fields(self):
        self.name_e.delete(0,'end'); self.dept_e.delete(0,'end')
        self.phone_e.delete(0,'end'); self.email_e.delete(0,'end')
        self.search_e.delete(0,'end')
        self.selected_id = None

    def update_member(self):
        if not hasattr(self, 'selected_id') or not self.selected_id:
            messagebox.showerror("Select", "Select a member to update")
            return
        name = self.name_e.get().strip()
        dept = self.dept_e.get().strip()
        phone = self.phone_e.get().strip()
        email = self.email_e.get().strip()
        if not name:
            messagebox.showerror("Validation", "Name is required")
            return
        q = "UPDATE members SET name=%s, department=%s, phone=%s, email=%s WHERE member_id=%s"
        res = self.execute(q, (name, dept, phone, email, self.selected_id))
        if res:
            messagebox.showinfo("Success", "Member updated")
            self.load_members()
            self.clear_fields()

    def delete_member(self):
        if not hasattr(self,'selected_id') or not self.selected_id:
            messagebox.showerror("Select", "Select a member to delete")
            return
        if not messagebox.askyesno("Confirm", "Delete selected member?"):
            return
        q = "DELETE FROM members WHERE member_id=%s"
        res = self.execute(q, (self.selected_id,))
        if res:
            messagebox.showinfo("Success", "Member deleted")
            self.load_members()
            self.clear_fields()

    def search_members(self):
        term = self.search_e.get().strip()
        if not term:
            messagebox.showerror("Input", "Enter search term")
            return
        q = "SELECT member_id, name, department, phone, email FROM members WHERE name LIKE %s OR email LIKE %s ORDER BY name"
        rows = self.execute(q, (f"%{term}%", f"%{term}%"), fetch=True)
        for r in self.tree.get_children():
            self.tree.delete(r)
        if rows:
            for row in rows:
                self.tree.insert("", "end", values=row)
