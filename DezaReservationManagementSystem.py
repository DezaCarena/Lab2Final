import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ==========================================
# DATABASE CONFIGURATION - HOTEL
# ==========================================
DB_NAME = "hotel_reservations.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_table():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                checkin_date TEXT NOT NULL,
                checkout_date TEXT NOT NULL,
                room_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                notes TEXT
            )
        """)

# ==========================================
# HOTEL RESERVATION SYSTEM - SUITE THEME
# ==========================================
class ReservationSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Reservation Management System")
        self.root.geometry("1150x700")
        self.root.minsize(950, 600)

        # COLOR CODES FROM IMAGE
        self.NAVY = "#0A1931"
        self.GOLD = "#D4AF37"
        self.DARK_GOLD = "#B8962E"
        self.CREAM = "#F5F0E8"
        self.WHITE = "#FFFFFF"

        self.selected_id = None
        self.configure_suite_theme()
        self.create_widgets()
        self.load_reservations()

    def configure_suite_theme(self):
        self.root.configure(bg=self.CREAM)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.CREAM)
        style.configure("TLabel", background=self.CREAM)
        style.configure("TLabelframe", background=self.CREAM)
        style.configure("TLabelframe.Label", background=self.CREAM, foreground=self.NAVY, font=("Arial", 10, "bold"))
        # Suite Table Color - Navy + Gold
        style.configure("Treeview.Heading", background=self.NAVY, foreground=self.GOLD, font=("Arial", 9, "bold"))
        style.map("Treeview.Heading", background=[("active", "#051025")])
        style.configure("Treeview", background=self.WHITE, fieldbackground=self.WHITE, rowheight=26)
        # Gold Buttons
        style.configure("Gold.TButton", background=self.GOLD, foreground=self.NAVY, font=("Arial", 9, "bold"))
        style.map("Gold.TButton", background=[("active", self.DARK_GOLD)])

    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="HOTEL RESERVATION MANAGEMENT SYSTEM",
            font=("Arial", 20, "bold"),
            bg=self.NAVY,
            fg=self.GOLD,
            pady=15
        )
        title.pack(fill="x")

        form = ttk.LabelFrame(self.root, text="Reservation Details", padding=12)
        form.pack(fill="x", padx=15, pady=10)

        ttk.Label(form, text="Customer Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = ttk.Entry(form, width=28)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Phone Number:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.phone_entry = ttk.Entry(form, width=25)
        self.phone_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Check-in Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(form, width=28)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Check-out Date (YYYY-MM-DD):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.time_entry = ttk.Entry(form, width=25)
        self.time_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(form, text="Room Type:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.guests_entry = ttk.Combobox(form, values=["Standard", "Deluxe", "Suite", "Presidential Suite"], width=26, state="readonly")
        self.guests_entry.grid(row=2, column=1, padx=5, pady=5)
        self.guests_entry.set("Suite")

        ttk.Label(form, text="Status:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.status_box = ttk.Combobox(form, values=["Pending", "Confirmed", "Checked-in", "Checked-out", "Cancelled", "Completed"], state="readonly", width=22)
        self.status_box.grid(row=2, column=3, padx=5, pady=5)
        self.status_box.set("Pending")

        ttk.Label(form, text="Notes:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.notes_entry = ttk.Entry(form, width=75)
        self.notes_entry.grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        buttons = ttk.Frame(self.root)
        buttons.pack(fill="x", padx=15, pady=5)
        ttk.Button(buttons, text="Add Reservation", style="Gold.TButton", command=self.add_reservation).pack(side="left", padx=4)
        ttk.Button(buttons, text="Update Selected", style="Gold.TButton", command=self.update_reservation).pack(side="left", padx=4)
        ttk.Button(buttons, text="Delete Selected", style="Gold.TButton", command=self.delete_reservation).pack(side="left", padx=4)
        ttk.Button(buttons, text="Clear Form", style="Gold.TButton", command=self.clear_form).pack(side="left", padx=4)

        search_frame = ttk.LabelFrame(self.root, text="Search Reservations", padding=10)
        search_frame.pack(fill="x", padx=15, pady=8)
        ttk.Label(search_frame, text="Name or Reservation ID:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=35)
        self.search_entry.pack(side="left", padx=5)
        ttk.Button(search_frame, text="Search", style="Gold.TButton", command=self.search_reservations).pack(side="left", padx=4)
        ttk.Button(search_frame, text="Show All", style="Gold.TButton", command=self.load_reservations).pack(side="left", padx=4)

        table_frame = ttk.LabelFrame(self.root, text="Reservation Records", padding=10)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 12))

        columns = ("id", "name", "phone", "date", "time", "guests", "status", "notes")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        headings = {"id": "ID", "name": "Customer Name", "phone": "Phone", "date": "Check-in", "time": "Check-out", "guests": "Room Type", "status": "Status", "notes": "Notes"}
        widths = {"id": 45, "name": 160, "phone": 110, "date": 100, "time": 100, "guests": 95, "status": 95, "notes": 200}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.select_reservation)

        self.count_label = ttk.Label(self.root, text="Total reservations: 0")
        self.count_label.pack(anchor="w", padx=20, pady=(0, 8))

    def get_form_data(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        checkin = self.date_entry.get().strip()
        checkout = self.time_entry.get().strip()
        room_type = self.guests_entry.get().strip()
        status = self.status_box.get()
        notes = self.notes_entry.get().strip()

        if not name or not phone or not checkin or not checkout:
            messagebox.showwarning("Missing Information", "Please complete name, phone, check-in and check-out.")
            return None
        try:
            datetime.strptime(checkin, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Check-in must be YYYY-MM-DD")
            return None
        try:
            datetime.strptime(checkout, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Check-out must be YYYY-MM-DD")
            return None
        return (name, phone, checkin, checkout, room_type, status, notes)

    def add_reservation(self):
        data = self.get_form_data()
        if data is None: return
        try:
            with connect_db() as conn:
                conn.execute("INSERT INTO reservations (customer_name, phone, checkin_date, checkout_date, room_type, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", data)
            messagebox.showinfo("Success", "Hotel reservation added successfully.")
            self.clear_form()
            self.load_reservations()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def load_reservations(self):
        self.display_records()

    def display_records(self, query=None, params=()):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            with connect_db() as conn:
                if query:
                    rows = conn.execute(query, params).fetchall()
                else:
                    rows = conn.execute("SELECT id, customer_name, phone, checkin_date, checkout_date, room_type, status, notes FROM reservations ORDER BY checkin_date").fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
            self.count_label.config(text=f"Total reservations: {len(rows)}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def search_reservations(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_reservations()
            return
        if keyword.isdigit():
            query = "SELECT id, customer_name, phone, checkin_date, checkout_date, room_type, status, notes FROM reservations WHERE customer_name LIKE ? OR id = ? ORDER BY checkin_date"
            params = (f"%{keyword}%", int(keyword))
        else:
            query = "SELECT id, customer_name, phone, checkin_date, checkout_date, room_type, status, notes FROM reservations WHERE customer_name LIKE ? ORDER BY checkin_date"
            params = (f"%{keyword}%",)
        self.display_records(query, params)

    def select_reservation(self, event=None):
        selected = self.tree.selection()
        if not selected: return
        values = self.tree.item(selected[0], "values")
        self.selected_id = int(values[0])
        self.name_entry.delete(0, tk.END); self.name_entry.insert(0, values[1])
        self.phone_entry.delete(0, tk.END); self.phone_entry.insert(0, values[2])
        self.date_entry.delete(0, tk.END); self.date_entry.insert(0, values[3])
        self.time_entry.delete(0, tk.END); self.time_entry.insert(0, values[4])
        self.guests_entry.set(values[5])
        self.status_box.set(values[6])
        self.notes_entry.delete(0, tk.END); self.notes_entry.insert(0, values[7] or "")

    def update_reservation(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a reservation from the table first.")
            return
        data = self.get_form_data()
        if data is None: return
        if not messagebox.askyesno("Confirm Update", "Do you want to update this reservation?"): return
        try:
            with connect_db() as conn:
                conn.execute("UPDATE reservations SET customer_name=?, phone=?, checkin_date=?, checkout_date=?, room_type=?, status=?, notes=? WHERE id=?", data + (self.selected_id,))
            messagebox.showinfo("Success", "Reservation updated successfully.")
            self.clear_form()
            self.load_reservations()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def delete_reservation(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a reservation from the table first.")
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this reservation?"): return
        try:
            with connect_db() as conn:
                conn.execute("DELETE FROM reservations WHERE id=?", (self.selected_id,))
            messagebox.showinfo("Success", "Reservation deleted successfully.")
            self.clear_form()
            self.load_reservations()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def clear_form(self):
        self.selected_id = None
        for entry in (self.name_entry, self.phone_entry, self.date_entry, self.time_entry, self.notes_entry, self.search_entry):
            entry.delete(0, tk.END)
        self.guests_entry.set("Suite")
        self.status_box.set("Pending")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

if __name__ == "__main__":
    create_table()
    root = tk.Tk()
    app = ReservationSystem(root)
    root.mainloop()
