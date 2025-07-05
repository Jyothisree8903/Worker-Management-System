import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import pandas as pd

def init_db():
    conn = sqlite3.connect('worker_mgmt.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, password TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE, gender TEXT, wage INTEGER,
        start_date TEXT, contact TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_id INTEGER, date TEXT,
        FOREIGN KEY(worker_id) REFERENCES workers(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_id INTEGER, amount INTEGER,
        date TEXT, paid_by TEXT,
        FOREIGN KEY(worker_id) REFERENCES workers(id),
        FOREIGN KEY(paid_by) REFERENCES users(username))''')
    conn.commit()
    conn.close()


class WorkerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Worker Management System")
        self.user = None
        self.login_screen()

    def login_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()
        tk.Label(self.root, text="Welcome", font=('Arial', 16),fg='red').pack(pady=10)
        tk.Label(self.root, text="Username").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()
        tk.Label(self.root, text="Password").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()
        tk.Button(self.root, text="Login", command=self.login).pack(pady=5)
        tk.Button(self.root, text="Register", command=self.register_screen).pack()

    def register_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()
        tk.Label(self.root, text="Register", font=('Arial', 16)).pack(pady=10)
        tk.Label(self.root, text="New Username").pack()
        self.new_username = tk.Entry(self.root)
        self.new_username.pack()
        tk.Label(self.root, text="Password").pack()
        self.new_password = tk.Entry(self.root, show="*")
        self.new_password.pack()
        tk.Button(self.root, text="Register", command=self.register_user).pack(pady=5)
        tk.Button(self.root, text="Back to Login", command=self.login_screen).pack()

    def login(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()
        conn = sqlite3.connect('worker_mgmt.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        result = c.fetchone()
        conn.close()
        if result:
            self.user = user
            self.dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def register_user(self):
        user = self.new_username.get()
        pwd = self.new_password.get()
        conn = sqlite3.connect('worker_mgmt.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users VALUES (?, ?)", (user, pwd))
            conn.commit()
            messagebox.showinfo("Success", "User registered")
            self.login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        conn.close()

    def dashboard(self):
        for widget in self.root.winfo_children(): widget.destroy()
        tk.Label(self.root, text=f"Welcome, {self.user}", font=('Arial', 14)).pack(pady=10)
        tk.Button(self.root, text="Add Worker", width=20, command=self.add_worker_screen).pack(pady=5)
        tk.Button(self.root, text="Mark Attendance", width=20, command=self.attendance_screen).pack(pady=5)
        tk.Button(self.root, text="Add Payment", width=20, command=self.payment_screen).pack(pady=5)
        tk.Button(self.root, text="View Report", width=20, command=self.report_screen).pack(pady=5)
        tk.Button(self.root, text="List All Workers", width=20, command=self.list_workers_screen).pack(pady=5)
        tk.Button(self.root, text="Manage Workers", width=20, command=self.manage_worker_screen).pack(pady=5)
        tk.Button(self.root, text="Logout", width=20, command=self.login_screen).pack(pady=10)

    def add_worker_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Add Worker")

        tk.Label(win, text="Name").grid(row=0, column=0)
        name = tk.Entry(win)
        name.grid(row=0, column=1)

        tk.Label(win, text="Gender (Male/Female)").grid(row=1, column=0)
        gender = tk.Entry(win)
        gender.grid(row=1, column=1)

        tk.Label(win, text="Start Date (YYYY-MM-DD)").grid(row=2, column=0)
        start_date = tk.Entry(win)
        start_date.grid(row=2, column=1)

        tk.Label(win, text="Contact Info").grid(row=3, column=0)
        contact = tk.Entry(win)
        contact.grid(row=3, column=1)

        def save():
            conn = sqlite3.connect('worker_mgmt.db')
            c = conn.cursor()
            c.execute("SELECT * FROM workers WHERE name=?", (name.get(),))
            if c.fetchone():
                messagebox.showwarning("Warning", "Worker already exists")
                conn.close()
                return
            wage = 1000 if gender.get().lower() == 'male' else 800
            c.execute("INSERT INTO workers (name, gender, wage, start_date, contact) VALUES (?, ?, ?, ?, ?)",
                      (name.get(), gender.get(), wage, start_date.get(), contact.get()))
            worker_id = c.lastrowid
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Worker added successfully.\nAssigned Worker ID is {worker_id}.")
            win.destroy()

        tk.Button(win, text="Save", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def list_workers_screen(self):
        win = tk.Toplevel(self.root)
        win.title("All Workers")
        tree = ttk.Treeview(win, columns=("ID", "Name", "Days", "Contact"), show='headings')
        tree.heading("ID", text="ID")
        tree.heading("Name", text="Name")
        tree.heading("Days", text="Days Worked")
        tree.heading("Contact", text="Contact Info")
        tree.pack(fill='both', expand=True)
        conn = sqlite3.connect('worker_mgmt.db')
        c = conn.cursor()
        c.execute("SELECT id, name, contact FROM workers")
        workers = c.fetchall()
        data_for_excel = []
        for w in workers:
            c.execute("SELECT COUNT(*) FROM attendance WHERE worker_id=?", (w[0],))
            days = c.fetchone()[0]
            tree.insert('', 'end', values=(w[0], w[1], days, w[2]))
            data_for_excel.append({'ID': w[0], 'Name': w[1], 'Days Worked': days, 'Contact': w[2]})
        pd.DataFrame(data_for_excel).to_excel("worker_data.xlsx", index=False)
        conn.close()

    def attendance_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Mark Attendance")

        tk.Label(win, text="Worker ID").pack()
        wid = tk.Entry(win)
        wid.pack()

        tk.Label(win, text="Date (YYYY-MM-DD)").pack()
        date = tk.Entry(win)
        date.insert(0, datetime.today().strftime('%Y-%m-%d'))
        date.pack()

        def mark():
            try:
                conn = sqlite3.connect('worker_mgmt.db')
                c = conn.cursor()

                # Check if worker ID exists
                c.execute("SELECT 1 FROM workers WHERE id=?", (int(wid.get()),))
                if not c.fetchone():
                    messagebox.showerror("Error", "Worker ID does not exist")
                    conn.close()
                    return

                # Check duplicate attendance
                c.execute("SELECT * FROM attendance WHERE worker_id=? AND date=?", (int(wid.get()), date.get()))
                if c.fetchone():
                    messagebox.showwarning("Warning", "Attendance already marked for this day")
                else:
                    c.execute("INSERT INTO attendance (worker_id, date) VALUES (?, ?)", (int(wid.get()), date.get()))
                    conn.commit()
                    messagebox.showinfo("Success", "Attendance marked successfully")
                    win.destroy()
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to mark attendance: {e}")

        tk.Button(win, text="Mark Attendance", command=mark).pack(pady=10)

    def payment_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Add Payment")
        tk.Label(win, text="Worker ID").pack()
        wid = tk.Entry(win)
        wid.pack()
        tk.Label(win, text="Amount").pack()
        amt = tk.Entry(win)
        amt.pack()
        tk.Label(win, text="Date (YYYY-MM-DD)").pack()
        date = tk.Entry(win)
        date.insert(0, datetime.today().strftime('%Y-%m-%d'))
        date.pack()

        def save_payment():
            try:
                conn = sqlite3.connect('worker_mgmt.db')
                c = conn.cursor()
                c.execute("INSERT INTO payments (worker_id, amount, date, paid_by) VALUES (?, ?, ?, ?)",
                          (int(wid.get()), int(amt.get()), date.get(), self.user))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Payment added")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")

        tk.Button(win, text="Submit", command=save_payment).pack(pady=10)

    def report_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Worker Report")
        tk.Label(win, text="Enter Worker ID").pack()
        wid = tk.Entry(win)
        wid.pack()
        output = tk.Text(win, width=60, height=20)
        output.pack()

        def fetch_report():
            output.delete(1.0, tk.END)
            try:
                conn = sqlite3.connect('worker_mgmt.db')
                c = conn.cursor()
                worker_id = int(wid.get())
                c.execute("SELECT name, gender, wage, start_date FROM workers WHERE id=?", (worker_id,))
                worker = c.fetchone()
                if not worker:
                    output.insert(tk.END, "Worker not found.\n")
                    return
                name, gender, wage, start = worker
                c.execute("SELECT COUNT(*) FROM attendance WHERE worker_id=?", (worker_id,))
                days_worked = c.fetchone()[0]
                total_wage = wage * days_worked
                c.execute("SELECT amount, date, paid_by FROM payments WHERE worker_id=?", (worker_id,))
                payments = c.fetchall()
                total_paid = sum(p[0] for p in payments)
                status = "Pending" if total_paid < total_wage else "Overpaid" if total_paid > total_wage else "Settled"
                balance = abs(total_paid - total_wage)
                output.insert(tk.END, f"Name: {name}\nGender: {gender}\nStart Date: {start}\nWage/Day: ₹{wage}\n")
                output.insert(tk.END, f"Days Worked: {days_worked}\nTotal Wage: ₹{total_wage}\n\n")
                output.insert(tk.END, f"Payments:\n")
                for amt, d, user in payments:
                    output.insert(tk.END, f"  ₹{amt} on {d} by {user}\n")
                output.insert(tk.END, f"\nTotal Paid: ₹{total_paid}\n{status} Amount: ₹{balance}\n")
                conn.close()
            except Exception as e:
                output.insert(tk.END, f"Error: {e}\n")

        tk.Button(win, text="Generate Report", command=fetch_report).pack(pady=5)

    def manage_worker_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Manage Workers")
        tk.Label(win, text="Worker ID").grid(row=0, column=0)
        wid = tk.Entry(win)
        wid.grid(row=0, column=1)
        tk.Label(win, text="New Gender").grid(row=1, column=0)
        gender = tk.Entry(win)
        gender.grid(row=1, column=1)
        tk.Label(win, text="New Start Date").grid(row=2, column=0)
        start = tk.Entry(win)
        start.grid(row=2, column=1)
        tk.Label(win, text="New Contact").grid(row=3, column=0)
        contact = tk.Entry(win)
        contact.grid(row=3, column=1)

        def update():
            try:
                wage = 1000 if gender.get().lower() == 'male' else 800
                conn = sqlite3.connect('worker_mgmt.db')
                c = conn.cursor()
                c.execute("UPDATE workers SET gender=?, wage=?, start_date=?, contact=? WHERE id=?",
                          (gender.get(), wage, start.get(), contact.get(), int(wid.get())))
                conn.commit()
                conn.close()
                messagebox.showinfo("Updated", "Worker info updated.")
            except Exception as e:
                messagebox.showerror("Error", f"{e}")

        def delete():
            try:
                confirm = messagebox.askyesno("Confirm", "Delete this worker and all related data?")
                if not confirm: return
                conn = sqlite3.connect('worker_mgmt.db')
                c = conn.cursor()
                c.execute("DELETE FROM attendance WHERE worker_id=?", (int(wid.get()),))
                c.execute("DELETE FROM payments WHERE worker_id=?", (int(wid.get()),))
                c.execute("DELETE FROM workers WHERE id=?", (int(wid.get()),))
                conn.commit()
                conn.close()
                messagebox.showinfo("Deleted", "Worker and records deleted.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"{e}")

        tk.Button(win, text="Update Worker", command=update).grid(row=4, column=0, pady=10)
        tk.Button(win, text="Delete Worker", command=delete).grid(row=4, column=1, pady=10)


if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    app = WorkerApp(root)
    root.mainloop()
