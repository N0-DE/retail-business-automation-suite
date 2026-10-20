"""
Damage Scanner UI
Allows cashiers / warehouse operators to scan damaged item barcodes.
Automatically resolves item name and vendor details from ERP databases,
and creates tracked return claims.
"""
from datetime import date
import customtkinter
import config

class DamageScannerApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Damage Entry Scanner")
        self.geometry("900x520")
        self.resizable(False, False)

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        self.current_slno = self.fetch_next_slno()
        self.setup_ui()

    def fetch_next_slno(self) -> int:
        conn = config.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT current_val FROM SLNO")
        row = cur.fetchone()
        next_val = (row[0] + 1) if row else 1001
        conn.close()
        return next_val

    def setup_ui(self):
        container = customtkinter.CTkFrame(self, corner_radius=15)
        container.pack(fill="both", expand=True, padx=25, pady=25)

        title = customtkinter.CTkLabel(
            container, 
            text="Damaged Goods & Return Claims Entry", 
            font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=(15, 20))

        # SLNO Display
        slno_frame = customtkinter.CTkFrame(container, fg_color="transparent")
        slno_frame.pack(fill="x", padx=40, pady=5)
        customtkinter.CTkLabel(slno_frame, text="Claim Ref ID (SLNO):", font=("Segoe UI", 15, "bold")).pack(side="left")
        self.slno_label = customtkinter.CTkLabel(slno_frame, text=f"#{self.current_slno}", font=("Segoe UI", 18, "bold"), text_color="#33cc66")
        self.slno_label.pack(side="left", padx=15)

        # Barcode Entry
        bc_frame = customtkinter.CTkFrame(container, fg_color="transparent")
        bc_frame.pack(fill="x", padx=40, pady=10)
        customtkinter.CTkLabel(bc_frame, text="Scan Barcode:", font=("Segoe UI", 14)).pack(side="left")
        self.barcode_entry = customtkinter.CTkEntry(bc_frame, placeholder_text="Scan or type barcode, then press Enter", width=350)
        self.barcode_entry.pack(side="left", padx=15)
        self.barcode_entry.bind("<Return>", self.lookup_barcode)
        self.barcode_entry.focus()

        # Item Name Display
        item_frame = customtkinter.CTkFrame(container, fg_color="transparent")
        item_frame.pack(fill="x", padx=40, pady=10)
        customtkinter.CTkLabel(item_frame, text="Resolved Item:", font=("Segoe UI", 14)).pack(side="left")
        self.item_entry = customtkinter.CTkEntry(item_frame, width=450)
        self.item_entry.pack(side="left", padx=15)

        # Supplier Display
        supp_frame = customtkinter.CTkFrame(container, fg_color="transparent")
        supp_frame.pack(fill="x", padx=40, pady=10)
        customtkinter.CTkLabel(supp_frame, text="Vendor / Supplier:", font=("Segoe UI", 14)).pack(side="left")
        self.supplier_entry = customtkinter.CTkEntry(supp_frame, width=450)
        self.supplier_entry.pack(side="left", padx=15)

        # Quantity Entry
        qty_frame = customtkinter.CTkFrame(container, fg_color="transparent")
        qty_frame.pack(fill="x", padx=40, pady=10)
        customtkinter.CTkLabel(qty_frame, text="Quantity Damaged:", font=("Segoe UI", 14)).pack(side="left")
        self.qty_entry = customtkinter.CTkEntry(qty_frame, width=120)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(side="left", padx=15)

        # Action Buttons
        btn_frame = customtkinter.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(pady=20)

        save_btn = customtkinter.CTkButton(
            btn_frame, 
            text="Save Return Claim (Alt+S)", 
            command=self.save_claim,
            fg_color="#1f538d",
            hover_color="#14375e",
            font=("Segoe UI", 14, "bold"),
            width=200,
            height=38
        )
        save_btn.pack(side="left", padx=10)
        self.bind("<Alt-s>", lambda e: self.save_claim())

        # Status Label
        self.status_label = customtkinter.CTkLabel(container, text="Ready. Scan barcode or try sample: 8901058852395", text_color="gray")
        self.status_label.pack(pady=5)

    def lookup_barcode(self, event=None):
        barcode = self.barcode_entry.get().strip()
        if not barcode:
            return

        conn = config.get_connection()
        cur = conn.cursor()

        # Lookup in ProductBatches joined with Parties
        query = """
        SELECT pb.RefItemName, p.PartyName
        FROM ProductBatches pb
        LEFT JOIN Parties p ON pb.SupplierLedgerID = p.LedgerID
        WHERE pb.ManualBarcode = ?
        """
        cur.execute(query, (barcode,))
        result = cur.fetchone()
        conn.close()

        if result:
            item_name, supplier = result
            self.item_entry.delete(0, "end")
            self.item_entry.insert(0, item_name or "")
            self.supplier_entry.delete(0, "end")
            self.supplier_entry.insert(0, supplier or "General Inventory")
            self.status_label.configure(text=f"Product found: {item_name}", text_color="#55ff55")
            self.qty_entry.focus()
        else:
            self.status_label.configure(text="Barcode not in ERP database. Enter details manually.", text_color="#ffbb33")
            self.item_entry.focus()

    def save_claim(self):
        barcode = self.barcode_entry.get().strip()
        item = self.item_entry.get().strip()
        supplier = self.supplier_entry.get().strip()
        qty = self.qty_entry.get().strip() or "1"
        today_str = str(date.today())

        if not item or not supplier:
            self.status_label.configure(text="Error: Item name and Supplier must not be empty.", text_color="#ff5555")
            return

        conn = config.get_connection()
        cur = conn.cursor()

        insert_sql = """
        INSERT INTO DAMAGE (slno, barcode, item_name, supplier, quantity, entry_date, cash, taken)
        VALUES (?, ?, ?, ?, ?, ?, 'no', 'no')
        """
        cur.execute(insert_sql, (self.current_slno, barcode, item, supplier, int(qty), today_str))

        # Update counter
        cur.execute("DELETE FROM SLNO")
        cur.execute("INSERT INTO SLNO (current_val) VALUES (?)", (self.current_slno,))
        conn.commit()
        conn.close()

        print(f"[+] Saved claim #{self.current_slno}: {item} ({supplier})")
        self.current_slno += 1
        self.slno_label.configure(text=f"#{self.current_slno}")

        # Reset fields
        self.barcode_entry.delete(0, "end")
        self.item_entry.delete(0, "end")
        self.supplier_entry.delete(0, "end")
        self.qty_entry.delete(0, "end")
        self.qty_entry.insert(0, "1")
        self.barcode_entry.focus()
        self.status_label.configure(text="Claim saved successfully! Ready for next scan.", text_color="#55ff55")

if __name__ == "__main__":
    app = DamageScannerApp()
    app.mainloop()
