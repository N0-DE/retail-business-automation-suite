"""
Weekly Payroll & Automated PDF Payslip Generator
Consolidates 6-day daily salary CSV records, calculates net weekly pay after advance/credit deductions,
and compiles professional, branded payslips in PDF format using FPDF.
"""
import csv
from datetime import date
from pathlib import Path
from fpdf import FPDF
import config

class PayslipPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 8, 'RETAIL STORE ENTERPRISES', align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', '', 10)
        self.cell(0, 5, 'Weekly Employee Payslip & Attendance Summary', align='C', new_x="LMARGIN", new_y="NEXT")
        self.line(10, 24, 70, 24)
        self.ln(6)

def generate_weekly_payslips(days_files: dict, credit_advances: dict = None):
    """
    Consolidates daily CSV records and generates weekly payslip PDFs.
    :param days_files: dict mapping day name -> CSV Path
    :param credit_advances: dict mapping employee name -> cash advance deduction
    """
    if credit_advances is None:
        credit_advances = {}

    weekly_totals = {}
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    # Initialize staff map
    for emp in config.DEFAULT_HOURLY_RATES.keys():
        weekly_totals[emp] = {d: 0 for d in day_names}

    # Aggregate daily salary logs
    for day, filepath in days_files.items():
        if not Path(filepath).exists():
            continue
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['Name']
                salary = int(float(row.get('TotalSalary', 0)))
                if name not in weekly_totals:
                    weekly_totals[name] = {d: 0 for d in day_names}
                weekly_totals[name][day] = salary

    # Generate Weekly Consolidated CSV
    export_csv = config.EXPORT_DIR / f"WeeklySummary_{date.today().strftime('%Y-%m-%d')}.csv"
    with open(export_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Employee'] + day_names + ['GrossPay', 'AdvanceDeduction', 'NetSalary']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for emp, days_data in weekly_totals.items():
            gross = sum(days_data.values())
            advance = credit_advances.get(emp, 0)
            net = max(0, gross - advance)

            row = {'Employee': emp}
            row.update(days_data)
            row['GrossPay'] = gross
            row['AdvanceDeduction'] = advance
            row['NetSalary'] = net
            writer.writerow(row)

    print(f"[+] Consolidated summary written: {export_csv}")

    # Generate Individual PDF Payslips
    pdf = PayslipPDF('P', 'mm', (80, 150))
    pdf.set_auto_page_break(auto=True, margin=5)

    for emp, days_data in weekly_totals.items():
        gross = sum(days_data.values())
        advance = credit_advances.get(emp, 0)
        net = max(0, gross - advance)

        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 6, f"Staff: {emp}", align='L', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 9)
        pdf.cell(0, 5, f"Date: {date.today().strftime('%d/%m/%Y')}", align='L', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Day-by-Day Breakdown Table
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(35, 6, 'Day', border=1)
        pdf.cell(25, 6, 'Earnings', border=1, align='R', new_x="LMARGIN", new_y="NEXT")

        pdf.set_font('Helvetica', '', 9)
        for day in day_names:
            pdf.cell(35, 5, day, border=1)
            pdf.cell(25, 5, str(days_data.get(day, 0)), border=1, align='R', new_x="LMARGIN", new_y="NEXT")

        pdf.ln(2)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(35, 6, 'Gross Total:', border=0)
        pdf.cell(25, 6, f"${gross}", border=0, align='R', new_x="LMARGIN", new_y="NEXT")

        pdf.cell(35, 5, 'Advance Deductions:', border=0)
        pdf.cell(25, 5, f"-${advance}", border=0, align='R', new_x="LMARGIN", new_y="NEXT")

        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(35, 6, 'Net Payable:', border=0)
        pdf.cell(25, 6, f"${net}", border=0, align='R', new_x="LMARGIN", new_y="NEXT")

    pdf_output = config.EXPORT_DIR / "payslips_compiled.pdf"
    pdf.output(str(pdf_output))
    print(f"[+] Compiled PDF payslips saved: {pdf_output}")

if __name__ == "__main__":
    sample_files = {
        'Monday': config.EXPORT_DIR / "DailySalary_Monday.csv",
        'Tuesday': config.EXPORT_DIR / "DailySalary_Tuesday.csv"
    }
    sample_advances = {"ALEX JOHNSON": 100, "BRIAN SMITH": 50}
    generate_weekly_payslips(sample_files, sample_advances)
