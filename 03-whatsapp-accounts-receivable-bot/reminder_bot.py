"""
WhatsApp Accounts Receivable & Payment Reminder Bot
Automates customer collection notices by reading AR aging Excel/CSV reports,
generating personalized notifications with remittance instructions, and dispatching
messages via Selenium WebDriver on WhatsApp Web.
"""
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import customtkinter
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import config

class ReminderBotGUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("WhatsApp Accounts Receivable Dispatcher")
        self.geometry("680x480")
        self.resizable(False, False)

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")

        self.selected_file = None
        self.attachment_file = None
        self.setup_ui()

    def setup_ui(self):
        container = customtkinter.CTkFrame(self, corner_radius=15)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        title = customtkinter.CTkLabel(
            container, 
            text="Automated WhatsApp Payment Reminder RPA", 
            font=("Segoe UI", 20, "bold")
        )
        title.pack(pady=(15, 10))

        subtitle = customtkinter.CTkLabel(
            container, 
            text="Parse customer debt aging sheets and dispatch personalized remittance notices", 
            font=("Segoe UI", 12),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 20))

        # File Selection Frame
        file_frame = customtkinter.CTkFrame(container, fg_color="transparent")
        file_frame.pack(fill="x", padx=40, pady=10)

        self.file_label = customtkinter.CTkLabel(file_frame, text="Aging Report: No file selected", font=("Segoe UI", 13))
        self.file_label.pack(side="left")

        choose_btn = customtkinter.CTkButton(
            file_frame, 
            text="Browse File (.csv, .xlsx)", 
            command=self.choose_file,
            width=180
        )
        choose_btn.pack(side="right")

        # Attachment Selection Frame (QR Code / Invoice)
        attach_frame = customtkinter.CTkFrame(container, fg_color="transparent")
        attach_frame.pack(fill="x", padx=40, pady=10)

        self.attach_label = customtkinter.CTkLabel(attach_frame, text="Attachment (Optional QR/Image): None", font=("Segoe UI", 13))
        self.attach_label.pack(side="left")

        choose_attach_btn = customtkinter.CTkButton(
            attach_frame, 
            text="Browse Image", 
            command=self.choose_attachment,
            width=180
        )
        choose_attach_btn.pack(side="right")

        # Mode Selection
        self.dry_run_var = customtkinter.StringVar(value="on")
        dry_run_check = customtkinter.CTkCheckBox(
            container, 
            text="Dry Run Mode (Simulate in terminal without launching Selenium)", 
            variable=self.dry_run_var,
            onvalue="on",
            offvalue="off"
        )
        dry_run_check.pack(pady=15)

        # Action Button
        self.run_btn = customtkinter.CTkButton(
            container, 
            text="Launch Reminder Dispatcher", 
            command=self.run_dispatcher,
            fg_color="#1f538d",
            hover_color="#14375e",
            font=("Segoe UI", 14, "bold"),
            height=42
        )
        self.run_btn.pack(pady=15)

        # Status Label
        self.status_label = customtkinter.CTkLabel(
            container, 
            text="Ready. Select an aging report to proceed.", 
            font=("Segoe UI", 12),
            text_color="gray"
        )
        self.status_label.pack(pady=5)

    def choose_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=str(config.BASE_DIR),
            title="Select Aging Report",
            filetypes=[("Data Files", "*.csv;*.xlsx;*.xls"), ("All Files", "*.*")]
        )
        if file_path:
            self.selected_file = Path(file_path)
            self.file_label.configure(text=f"Report: {self.selected_file.name}")
            self.status_label.configure(text=f"Loaded {self.selected_file.name}", text_color="#55ff55")

    def choose_attachment(self):
        file_path = filedialog.askopenfilename(
            initialdir=str(config.BASE_DIR),
            title="Select Payment QR or Attachment",
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.webp"), ("All Files", "*.*")]
        )
        if file_path:
            self.attachment_file = Path(file_path)
            self.attach_label.configure(text=f"Attachment: {self.attachment_file.name}")

    def run_dispatcher(self):
        report_file = self.selected_file or config.SAMPLE_REPORT_PATH
        if not report_file.exists():
            self.status_label.configure(text="Error: Report file not found.", text_color="#ff5555")
            return

        is_dry_run = self.dry_run_var.get() == "on"
        self.status_label.configure(text="Dispatching payment reminders...", text_color="#33ccff")
        self.update_idletasks()

        # Load Template
        with open(config.TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template = f.read()

        # Load Data
        df = pd.read_excel(report_file) if str(report_file).endswith((".xlsx", ".xls")) else pd.read_csv(report_file)

        # Standardize column naming
        cols = {c.lower(): c for c in df.columns}
        name_col = cols.get("customername") or cols.get("name") or cols.get("party") or df.columns[0]
        phone_col = cols.get("mobilephone") or cols.get("phone") or cols.get("mobile") or df.columns[1]
        balance_col = cols.get("duebalance") or cols.get("balance") or cols.get("totalbalance") or df.columns[2]

        print(f"\n[*] Processing {len(df)} customer records from {report_file.name} (Dry Run = {is_dry_run})")

        if is_dry_run:
            for _, row in df.iterrows():
                customer = str(row[name_col])
                phone = str(row[phone_col]).replace(".0", "").replace("+", "").strip()
                balance = f"${float(row[balance_col]):,.2f}"

                personalized_msg = template.format(
                    CustomerName=customer,
                    CompanyName=config.COMPANY_NAME,
                    BalanceAmount=balance,
                    BankAccountName=config.BANK_ACCOUNT_NAME,
                    BankAccountNumber=config.BANK_ACCOUNT_NUMBER,
                    BankRouting=config.BANK_ROUTING,
                    ContactPhone=config.CONTACT_PHONE
                )
                print(f"\n--- [DRY RUN SIMULATION] To: +{config.COUNTRY_DIAL_CODE}{phone} ({customer}) ---")
                print(personalized_msg[:200] + "...\n")
            self.status_label.configure(text="Dry run complete! Check terminal output.", text_color="#55ff55")
            return

        # Live Selenium Execution
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get("https://web.whatsapp.com")
            
            self.status_label.configure(text="Please scan QR code in WhatsApp browser window...", text_color="#ffbb33")
            time.sleep(config.LOGIN_WAIT_SECONDS)

            for _, row in df.iterrows():
                customer = str(row[name_col])
                phone = str(row[phone_col]).replace(".0", "").replace("+", "").strip()
                balance = f"${float(row[balance_col]):,.2f}"

                if not phone.isdigit() or len(phone) < 7:
                    print(f"[-] Skipping invalid contact: {customer} ({phone})")
                    continue

                msg = template.format(
                    CustomerName=customer,
                    CompanyName=config.COMPANY_NAME,
                    BalanceAmount=balance,
                    BankAccountName=config.BANK_ACCOUNT_NAME,
                    BankAccountNumber=config.BANK_ACCOUNT_NUMBER,
                    BankRouting=config.BANK_ROUTING,
                    ContactPhone=config.CONTACT_PHONE
                )

                link = f"https://web.whatsapp.com/send?phone=+{config.COUNTRY_DIAL_CODE}{phone}"
                driver.get(link)
                time.sleep(6)

                try:
                    msg_box = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, '//footer//div[@contenteditable="true"]'))
                    )
                    for line in msg.split("\n"):
                        msg_box.send_keys(line)
                        msg_box.send_keys(Keys.SHIFT, Keys.ENTER)
                    msg_box.send_keys(Keys.ENTER)
                    print(f"[+] Sent dues reminder to {customer} ({phone})")
                    time.sleep(config.MESSAGE_DELAY_SECONDS)
                except Exception as ex:
                    print(f"[-] Could not send to {customer}: {ex}")

            driver.quit()
            self.status_label.configure(text="All reminders dispatched successfully!", text_color="#55ff55")
        except Exception as e:
            self.status_label.configure(text=f"Automation error: {e}", text_color="#ff5555")

if __name__ == "__main__":
    app = ReminderBotGUI()
    app.mainloop()
