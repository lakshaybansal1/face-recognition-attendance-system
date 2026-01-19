"""
Face Recognition Attendance System - Student Management Module
Author: Lakshay Bansal
University at Albany - Computer Science

Description:
Tkinter-based GUI for managing student records stored in
Firebase Realtime Database. Supports add, update, delete,
and export operations.

This file has been refactored and customized by Lakshay Bansal.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import datetime
import firebase_admin
from firebase_admin import credentials, db


# -------------------- Firebase Initialization --------------------

def initialize_firebase():
    """Initialize Firebase connection using service account credentials."""
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://facerecognitonattendance-default-rtdb.firebaseio.com/"
        })


initialize_firebase()
students_ref = db.reference("Students")


# -------------------- Main Application Class --------------------

class AttendanceManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Attendance Management Panel")
        self.root.geometry("900x600")

        self.data_frame = pd.DataFrame()

        self.build_ui()
        self.refresh_table()

    # -------------------- UI Construction --------------------

    def build_ui(self):
        """Create and arrange all GUI components."""

        title_label = tk.Label(
            self.root,
            text="Attendance Management Panel",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        # Table View
        self.table = ttk.Treeview(
            self.root,
            columns=("name", "id", "branch", "status", "total", "last_time"),
            show="headings"
        )

        headings = [
            ("name", "NAME"),
            ("id", "ID"),
            ("branch", "BRANCH"),
            ("status", "STATUS"),
            ("total", "TOTAL"),
            ("last_time", "LAST MARKED")
        ]

        for key, title in headings:
            self.table.heading(key, text=title)

        self.table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Input Fields Frame
        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=10)

        self._create_form_fields(form_frame)
        self._create_buttons()

        self.table.bind("<ButtonRelease-1>", self.load_selected_record)

    def _create_form_fields(self, parent):
        """Create input form fields."""

        labels = ["Student ID", "Name", "Branch", "Status", "Total Attendance"]
        for i, text in enumerate(labels):
            tk.Label(parent, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")

        self.id_entry = tk.Entry(parent)
        self.name_entry = tk.Entry(parent)
        self.branch_entry = tk.Entry(parent)
        self.total_entry = tk.Entry(parent)

        self.status_var = tk.StringVar()
        self.status_menu = tk.OptionMenu(parent, self.status_var, "P", "A", "E")

        self.id_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        self.branch_entry.grid(row=2, column=1, padx=5, pady=5)
        self.status_menu.grid(row=3, column=1, padx=5, pady=5)
        self.total_entry.grid(row=4, column=1, padx=5, pady=5)

    def _create_buttons(self):
        """Create action buttons."""

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add", width=12, command=self.add_record).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Update", width=12, command=self.update_record).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", width=12, command=self.delete_record).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Export", width=12, command=self.export_records).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear", width=12, command=self.clear_form).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Quit", width=12, command=self.root.quit).pack(side=tk.LEFT, padx=5)

    # -------------------- Data Handling --------------------

    def fetch_records(self) -> pd.DataFrame:
        """Fetch student records from Firebase and return as DataFrame."""
        try:
            raw_data = students_ref.get()
            if not raw_data:
                return pd.DataFrame(columns=["name", "id", "branch", "status", "total", "last_time"])

            df = pd.DataFrame.from_dict(raw_data, orient="index")
            df = df.reindex(columns=[
                "name", "id", "branch",
                "attendance", "total_attendance", "last_attendance_time"
            ])

            df.columns = ["name", "id", "branch", "status", "total", "last_time"]
            return df

        except Exception as error:
            print("Error loading data:", error)
            return pd.DataFrame(columns=["name", "id", "branch", "status", "total", "last_time"])

    def refresh_table(self):
        """Reload table data from Firebase."""
        self.data_frame = self.fetch_records()

        for row in self.table.get_children():
            self.table.delete(row)

        for _, row in self.data_frame.iterrows():
            self.table.insert("", tk.END, values=row.tolist())

    # -------------------- Event Handlers --------------------

    def load_selected_record(self, event):
        """Load selected row into input fields."""
        selected = self.table.selection()
        if not selected:
            return

        values = self.table.item(selected[0])["values"]

        self.clear_form()

        self.id_entry.insert(0, values[1])
        self.name_entry.insert(0, values[0])
        self.branch_entry.insert(0, values[2])
        self.status_var.set(values[3])
        self.total_entry.insert(0, values[4])

    def add_record(self):
        """Add a new student record to Firebase."""
        student_id = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        branch = self.branch_entry.get().strip()
        status = self.status_var.get()
        total = self.total_entry.get()

        if not student_id or not name or not branch:
            messagebox.showerror("Input Error", "Student ID, Name, and Branch are required.")
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status in ["P", "E"] else "N/A"

        record = {
            "name": name,
            "id": student_id,
            "branch": branch,
            "attendance": status,
            "total_attendance": int(total) if total else 0,
            "last_attendance_time": timestamp
        }

        students_ref.child(student_id).set(record)
        self.refresh_table()

    def update_record(self):
        """Update an existing student record."""
        student_id = self.id_entry.get().strip()
        if not student_id:
            messagebox.showerror("Input Error", "Student ID is required.")
            return

        current = students_ref.child(student_id).get() or {}

        updated = {
            "name": self.name_entry.get() or current.get("name"),
            "id": student_id,
            "branch": self.branch_entry.get() or current.get("branch"),
            "attendance": self.status_var.get() or current.get("attendance"),
            "total_attendance": int(self.total_entry.get()) if self.total_entry.get() else current.get("total_attendance", 0),
            "last_attendance_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        students_ref.child(student_id).set(updated)
        self.refresh_table()

    def delete_record(self):
        """Delete a student record."""
        student_id = self.id_entry.get().strip()
        if not student_id:
            messagebox.showerror("Input Error", "Student ID is required.")
            return

        students_ref.child(student_id).delete()
        self.refresh_table()
        self.clear_form()

    def export_records(self):
        """Export current table data to an Excel file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )

        if file_path:
            self.data_frame.to_excel(file_path, index=False)
            messagebox.showinfo("Export Successful", "Data exported successfully.")

    def clear_form(self):
        """Clear all input fields."""
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.branch_entry.delete(0, tk.END)
        self.status_var.set("")
        self.total_entry.delete(0, tk.END)


# -------------------- App Launcher --------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceManager(root)
    root.mainloop()
