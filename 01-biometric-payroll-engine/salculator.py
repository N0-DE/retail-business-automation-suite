"""
Salculator: Daily Biometric Payroll & Shift Calculator
Provides a modern CustomTkinter interface for daily wage computation, loader surcharge distribution,
and automated daily CSV reconciliation.
"""
import csv
import math
from pathlib import Path
import customtkinter
import config

def round_currency(number: float) -> int:
    """Rounds float amounts to nearest whole currency unit."""
    string = str(number)
    splitter = string.split(".")
    base = int(splitter[0])
    if len(splitter) > 1 and int(splitter[1][0]) >= 5:
        base += 1
    return base

class SalculatorApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Salculator - Biometric Daily Payroll")
        self.geometry("640x520")
        self.resizable(False, False)
        
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")

        self.hourly_rates = config.DEFAULT_HOURLY_RATES
        self.active_loaders = set(config.DEFAULT_LOADERS)
        self.selected_day = "Monday"
        self.loading_charge = 0.0

        self.setup_ui()

    def setup_ui(self):
        self.container = customtkinter.CTkFrame(self, corner_radius=15)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = customtkinter.CTkLabel(
            self.container, 
            text="Biometric Daily Payroll Calculator", 
            font=("Segoe UI", 22, "bold")
        )
        title_label.pack(pady=(20, 10))

        # Day Selector
        day_label = customtkinter.CTkLabel(self.container, text="Select Work Day:", font=("Segoe UI", 14))
        day_label.pack(pady=(5, 2))
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        self.day_combobox = customtkinter.CTkComboBox(
            self.container, 
            values=days, 
            width=220
        )
        self.day_combobox.pack(pady=(0, 15))

        # Loading Charge Entry
        charge_label = customtkinter.CTkLabel(self.container, text="Total Daily Loading Charge ($ / ₹):", font=("Segoe UI", 14))
        charge_label.pack(pady=(5, 2))
        self.charge_entry = customtkinter.CTkEntry(
            self.container, 
            placeholder_text="e.g. 500", 
            width=220
        )
        self.charge_entry.pack(pady=(0, 15))

        # Active Loaders Selection Frame
        loader_frame_label = customtkinter.CTkLabel(self.container, text="Active Loaders Present Today:", font=("Segoe UI", 14))
        loader_frame_label.pack(pady=(5, 2))

        self.loader_checkboxes = {}
        checkbox_frame = customtkinter.CTkFrame(self.container, fg_color="transparent")
        checkbox_frame.pack(pady=(0, 15))

        for loader in config.DEFAULT_LOADERS:
            var = customtkinter.StringVar(value="on")
            cb = customtkinter.CTkCheckBox(
                checkbox_frame, 
                text=loader, 
                variable=var, 
                onvalue="on", 
                offvalue="off"
            )
            cb.pack(side="left", padx=10)
            self.loader_checkboxes[loader] = var

        # Action Button
        self.calc_button = customtkinter.CTkButton(
            self.container, 
            text="Compute & Export Payroll", 
            command=self.calculate_payroll,
            fg_color="#1f538d",
            hover_color="#14375e",
            font=("Segoe UI", 15, "bold"),
            height=40
        )
        self.calc_button.pack(pady=20)

        # Status Label
        self.status_label = customtkinter.CTkLabel(
            self.container, 
            text="Ready to process biometric logs", 
            font=("Segoe UI", 12),
            text_color="gray"
        )
        self.status_label.pack(pady=(0, 10))

    def calculate_payroll(self):
        day = self.day_combobox.get()
        charge_raw = self.charge_entry.get().strip()

        try:
            loading_charge = float(charge_raw) if charge_raw else 0.0
        except ValueError:
            self.status_label.configure(text="Error: Invalid loading charge amount.", text_color="#ff5555")
            return

        active_loaders = [name for name, var in self.loader_checkboxes.items() if var.get() == "on"]
        attendance_file = config.DEFAULT_ATTENDANCE_FILE

        if not attendance_file.exists():
            self.status_label.configure(text=f"Error: Missing attendance file at {attendance_file}", text_color="#ff5555")
            return

        output_file = config.EXPORT_DIR / f"DailySalary_{day}.csv"

        try:
            with open(attendance_file, "r", encoding="utf-8") as f_in, open(output_file, "w", newline="", encoding="utf-8") as f_out:
                reader = csv.DictReader(f_in)
                fieldnames = ['EmployeeCode', 'Name', 'InTime', 'OutTime', 'TotalHours', 'BaseSalary', 'LoadingShare', 'TotalSalary']
                writer = csv.DictWriter(f_out, fieldnames=fieldnames)
                writer.writeheader()

                total_records = 0
                for row in reader:
                    name = row.get('EmployeeName') or row.get('Name', 'Unknown')
                    code = row.get('EmployeeCode', '')
                    in_time = row.get('InTime', '--')
                    out_time = row.get('OutTime', '--')
                    time_str = row.get('TotalHours', '00:00')

                    # Parse HH:MM
                    time_parts = time_str.split(":")
                    hours = int(time_parts[0]) if len(time_parts) > 0 else 0
                    mins = int(time_parts[1]) if len(time_parts) > 1 else 0
                    decimal_hours = hours + (mins / 60.0)

                    rate = self.hourly_rates.get(name, 50.0)
                    base_salary = round_currency(decimal_hours * rate)

                    # Split 50% loading surcharge equally among active loaders
                    loading_share = 0
                    if name in active_loaders and len(active_loaders) > 0:
                        loading_share = round_currency((loading_charge * 0.5) / len(active_loaders))

                    total_salary = base_salary + loading_share
                    writer.writerow({
                        'EmployeeCode': code,
                        'Name': name,
                        'InTime': in_time,
                        'OutTime': out_time,
                        'TotalHours': time_str,
                        'BaseSalary': base_salary,
                        'LoadingShare': loading_share,
                        'TotalSalary': total_salary
                    })
                    total_records += 1

            self.status_label.configure(
                text=f"Success: Processed {total_records} records -> {output_file.name}", 
                text_color="#55ff55"
            )
        except Exception as e:
            self.status_label.configure(text=f"Processing failed: {str(e)}", text_color="#ff5555")

if __name__ == "__main__":
    app = SalculatorApp()
    app.mainloop()
