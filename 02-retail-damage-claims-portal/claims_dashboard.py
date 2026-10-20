"""
Claims Settlement & Reconciliation Dashboard
Interactive ttk.Treeview table where warehouse managers filter damaged stock by supplier,
track returns to reps ("TAKEN"), record supplier credit refunds ("CASH"), and archive settled claims.
"""
import tkinter as tk
from tkinter import ttk
import customtkinter
import config

class ClaimsDashboardApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Claims Settlement & Vendor Reconciliation Dashboard")
        self.geometry("1100x680")

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        self.setup_ui()
        self.load_suppliers()
        self.load_claims_data()

    def setup_ui(self):
        # Header Controls
        header_frame = customtkinter.CTkFrame(self, corner_radius=10)
        header_frame.pack(fill="x", padx=15, pady=15)

        title = customtkinter.CTkLabel(
            header_frame, 
            text="Damaged Inventory Reconciliation & Settlement", 
            font=("Segoe UI", 20, "bold")
        )
        title.pack(side="left", padx=15, pady=10)

        # Supplier Filter
        self.supplier_var = customtkinter.StringVar(value="All Suppliers")
        self.supplier_dropdown = customtkinter.CTkOptionMenu(
            header_frame,
            variable=self.supplier_var,
            values=["All Suppliers"],
            command=self.filter_by_supplier,
            width=220
        )
        self.supplier_dropdown.pack(side="right", padx=15, pady=10)
        customtkinter.CTkLabel(header_frame, text="Filter Vendor:", font=("Segoe UI", 13)).pack(side="right", padx=5)

        # Treeview Container
        tree_frame = customtkinter.CTkFrame(self, corner_radius=10)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=5)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="white",
            rowheight=28,
            fieldbackground="#2b2b2b",
            borderwidth=0
        )
        style.map("Treeview", background=[("selected", "#1f538d")])
        style.configure("Treeview.Heading", background="#3a3a3a", foreground="white", font=("Segoe UI", 11, "bold"))

        columns = ("Slno", "Barcode", "ItemName", "Supplier", "Quantity", "Date", "CashRefund", "VendorTaken")
        self.treeview = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        self.treeview.heading("Slno", text="Ref #")
        self.treeview.heading("Barcode", text="Barcode")
        self.treeview.heading("ItemName", text="Product Description")
        self.treeview.heading("Supplier", text="Vendor / Supplier")
        self.treeview.heading("Quantity", text="Qty")
        self.treeview.heading("Date", text="Recorded Date")
        self.treeview.heading("CashRefund", text="Credit Issued?")
        self.treeview.heading("VendorTaken", text="Goods Returned?")

        self.treeview.column("Slno", width=70, anchor="center")
        self.treeview.column("Barcode", width=140, anchor="center")
        self.treeview.column("ItemName", width=300, anchor="w")
        self.treeview.column("Supplier", width=200, anchor="w")
        self.treeview.column("Quantity", width=60, anchor="center")
        self.treeview.column("Date", width=110, anchor="center")
        self.treeview.column("CashRefund", width=100, anchor="center")
        self.treeview.column("VendorTaken", width=110, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.treeview.pack(fill="both", expand=True, padx=5, pady=5)

        # Bottom Actions Bar
        action_frame = customtkinter.CTkFrame(self, corner_radius=10)
        action_frame.pack(fill="x", padx=15, pady=15)

        customtkinter.CTkButton(
            action_frame, 
            text="Mark CASH / Credit Settled", 
            command=self.mark_cash,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            font=("Segoe UI", 13, "bold"),
            width=180
        ).pack(side="left", padx=10, pady=10)

        customtkinter.CTkButton(
            action_frame, 
            text="Mark TAKEN by Supplier Rep", 
            command=self.mark_taken,
            fg_color="#0277bd",
            hover_color="#01579b",
            font=("Segoe UI", 13, "bold"),
            width=190
        ).pack(side="left", padx=10, pady=10)

        customtkinter.CTkButton(
            action_frame, 
            text="Archive Fully Settled Claims", 
            command=self.archive_settled,
            fg_color="#c62828",
            hover_color="#8e0000",
            font=("Segoe UI", 13, "bold"),
            width=180
        ).pack(side="right", padx=10, pady=10)

    def load_suppliers(self):
        conn = config.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT supplier FROM DAMAGE WHERE supplier IS NOT NULL")
        rows = cur.fetchall()
        conn.close()

        suppliers = ["All Suppliers"] + [r[0] for r in rows if r[0]]
        self.supplier_dropdown.configure(values=suppliers)

    def load_claims_data(self, supplier_filter=None):
        self.treeview.delete(*self.treeview.get_children())
        conn = config.get_connection()
        cur = conn.cursor()

        if supplier_filter and supplier_filter != "All Suppliers":
            cur.execute("SELECT slno, barcode, item_name, supplier, quantity, entry_date, cash, taken FROM DAMAGE WHERE supplier = ? ORDER BY slno DESC", (supplier_filter,))
        else:
            cur.execute("SELECT slno, barcode, item_name, supplier, quantity, entry_date, cash, taken FROM DAMAGE ORDER BY slno DESC")

        records = cur.fetchall()
        conn.close()

        for rec in records:
            self.treeview.insert("", "end", values=rec)

    def filter_by_supplier(self, choice):
        self.load_claims_data(choice)

    def get_selected_slno(self):
        selected = self.treeview.selection()
        if not selected:
            return None
        values = self.treeview.item(selected[0], "values")
        return values[0]

    def mark_cash(self):
        slno = self.get_selected_slno()
        if not slno:
            return
        conn = config.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE DAMAGE SET cash = 'yes' WHERE slno = ?", (slno,))
        conn.commit()
        conn.close()
        self.load_claims_data(self.supplier_var.get())

    def mark_taken(self):
        slno = self.get_selected_slno()
        if not slno:
            return
        conn = config.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE DAMAGE SET taken = 'yes' WHERE slno = ?", (slno,))
        conn.commit()
        conn.close()
        self.load_claims_data(self.supplier_var.get())

    def archive_settled(self):
        """Archives rows where both cash and goods return are fully settled."""
        conn = config.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM DAMAGE WHERE cash = 'yes' AND taken = 'yes'")
        conn.commit()
        conn.close()
        print("[+] Fully reconciled claims archived.")
        self.load_claims_data(self.supplier_var.get())

if __name__ == "__main__":
    app = ClaimsDashboardApp()
    app.mainloop()
