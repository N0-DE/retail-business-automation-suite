"""
Cash Drawer Balancing & End-of-Day Audit Dashboard
CustomTkinter financial reconciliation interface. Computes net register cash
across 5 POS cash registers, matches against digital settlement receipts (UPI, Card, Bank),
factors in petty cash expenses, and displays real-time drawer variance (shortage/excess).
"""
import customtkinter
import config

class CashAuditApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("End-of-Day Cash Drawer Audit & Reconciliation")
        self.geometry("920x620")
        self.resizable(False, False)

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")

        self.setup_ui()
        self.calculate_reconciliation()

    def setup_ui(self):
        # Header
        header = customtkinter.CTkFrame(self, corner_radius=10)
        header.pack(fill="x", padx=20, pady=15)

        title = customtkinter.CTkLabel(
            header, 
            text="Cash Desk Balancing & POS Reconciliation Dashboard", 
            font=("Segoe UI", 20, "bold")
        )
        title.pack(side="left", padx=15, pady=10)

        # Main Layout: 2 Columns (Left: Counter Totals, Right: Digital Remittances & Variances)
        content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # Left Column - Registers
        left_col = customtkinter.CTkFrame(content_frame, corner_radius=12)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        customtkinter.CTkLabel(left_col, text="POS Register Balances", font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Opening Balance
        ob_frame = customtkinter.CTkFrame(left_col, fg_color="transparent")
        ob_frame.pack(fill="x", padx=20, pady=5)
        customtkinter.CTkLabel(ob_frame, text="Opening Balance:", font=("Segoe UI", 13)).pack(side="left")
        self.ob_entry = customtkinter.CTkEntry(ob_frame, width=140)
        self.ob_entry.insert(0, str(config.DEFAULT_OPENING_BALANCE))
        self.ob_entry.pack(side="right")
        self.ob_entry.bind("<KeyRelease>", lambda e: self.calculate_reconciliation())

        self.counter_entries = {}
        for counter_name, default_val in config.SAMPLE_COUNTER_BALANCES.items():
            f = customtkinter.CTkFrame(left_col, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=5)
            customtkinter.CTkLabel(f, text=f"{counter_name}:", font=("Segoe UI", 13)).pack(side="left")
            entry = customtkinter.CTkEntry(f, width=140)
            entry.insert(0, str(default_val))
            entry.pack(side="right")
            entry.bind("<KeyRelease>", lambda e: self.calculate_reconciliation())
            self.counter_entries[counter_name] = entry

        # Total System Expected
        total_exp_frame = customtkinter.CTkFrame(left_col, fg_color="#1f538d", corner_radius=8)
        total_exp_frame.pack(fill="x", padx=20, pady=15)
        customtkinter.CTkLabel(total_exp_frame, text="Expected Total:", font=("Segoe UI", 14, "bold")).pack(side="left", padx=10, pady=8)
        self.expected_label = customtkinter.CTkLabel(total_exp_frame, text="$0.00", font=("Segoe UI", 15, "bold"))
        self.expected_label.pack(side="right", padx=10, pady=8)

        # Right Column - Physical & Remittances
        right_col = customtkinter.CTkFrame(content_frame, corner_radius=12)
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        customtkinter.CTkLabel(right_col, text="Remittances & Physical Counts", font=("Segoe UI", 16, "bold")).pack(pady=10)

        remittance_items = [
            ("Digital Payments (UPI / GPay)", "25400.00"),
            ("Card Swipe (HDFC / POS)", "38200.00"),
            ("Petty Cash Expenses", "4500.00"),
            ("Bank Cash Drop", "15000.00"),
            ("Cash Drawer Physical Count", "27170.00")
        ]

        self.remittance_entries = {}
        for label_text, default_val in remittance_items:
            f = customtkinter.CTkFrame(right_col, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=5)
            customtkinter.CTkLabel(f, text=label_text, font=("Segoe UI", 13)).pack(side="left")
            entry = customtkinter.CTkEntry(f, width=140)
            entry.insert(0, default_val)
            entry.pack(side="right")
            entry.bind("<KeyRelease>", lambda e: self.calculate_reconciliation())
            self.remittance_entries[label_text] = entry

        # Total Physical / Remitted Count
        total_act_frame = customtkinter.CTkFrame(right_col, fg_color="#2e7d32", corner_radius=8)
        total_act_frame.pack(fill="x", padx=20, pady=10)
        customtkinter.CTkLabel(total_act_frame, text="Accounted Total:", font=("Segoe UI", 14, "bold")).pack(side="left", padx=10, pady=8)
        self.accounted_label = customtkinter.CTkLabel(total_act_frame, text="$0.00", font=("Segoe UI", 15, "bold"))
        self.accounted_label.pack(side="right", padx=10, pady=8)

        # Discrepancy Card
        self.diff_card = customtkinter.CTkFrame(right_col, corner_radius=10, border_width=2)
        self.diff_card.pack(fill="x", padx=20, pady=10)
        customtkinter.CTkLabel(self.diff_card, text="Variance / Cash Discrepancy:", font=("Segoe UI", 13, "bold")).pack(side="left", padx=15, pady=12)
        self.diff_label = customtkinter.CTkLabel(self.diff_card, text="$0.00", font=("Segoe UI", 16, "bold"))
        self.diff_label.pack(side="right", padx=15, pady=12)

    def calculate_reconciliation(self):
        try:
            ob = float(self.ob_entry.get().strip() or 0)
            counter_sum = sum(float(e.get().strip() or 0) for e in self.counter_entries.values())
            expected_total = ob + counter_sum
            self.expected_label.configure(text=f"${expected_total:,.2f}")

            accounted_total = sum(float(e.get().strip() or 0) for e in self.remittance_entries.values())
            self.accounted_label.configure(text=f"${accounted_total:,.2f}")

            variance = accounted_total - expected_total

            if abs(variance) < 0.01:
                self.diff_card.configure(border_color="#2e7d32", fg_color="#1b5e20")
                self.diff_label.configure(text="BALANCED ($0.00)", text_color="#55ff55")
            elif variance > 0:
                self.diff_card.configure(border_color="#0277bd", fg_color="#01579b")
                self.diff_label.configure(text=f"SURPLUS (+${variance:,.2f})", text_color="#33ccff")
            else:
                self.diff_card.configure(border_color="#c62828", fg_color="#8e0000")
                self.diff_label.configure(text=f"SHORTAGE (-${abs(variance):,.2f})", text_color="#ff5555")
        except ValueError:
            pass

if __name__ == "__main__":
    app = CashAuditApp()
    app.mainloop()
