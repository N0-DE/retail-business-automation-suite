"""
Configuration module for WhatsApp AR Reminder Bot.
Loads remittance details and rate-limiting timings safely from environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

COMPANY_NAME = os.getenv("COMPANY_NAME", "Acme Retail & Wholesale")
CONTACT_PHONE = os.getenv("CONTACT_PHONE", "+1 555-019-2834")

BANK_ACCOUNT_NAME = os.getenv("BANK_ACCOUNT_NAME", "Acme Retail Store LLC")
BANK_ACCOUNT_NUMBER = os.getenv("BANK_ACCOUNT_NUMBER", "123456789012")
BANK_ROUTING = os.getenv("BANK_IFSC_OR_ROUTING", "ROUT0001234")

COUNTRY_DIAL_CODE = os.getenv("COUNTRY_DIAL_CODE", "1")
LOGIN_WAIT_SECONDS = int(os.getenv("LOGIN_WAIT_SECONDS", "45"))
MESSAGE_DELAY_SECONDS = int(os.getenv("MESSAGE_DELAY_SECONDS", "10"))

TEMPLATE_PATH = BASE_DIR / "templates" / "message_template.txt"
SAMPLE_REPORT_PATH = BASE_DIR / "sample_data" / "sample_aging_report.csv"
