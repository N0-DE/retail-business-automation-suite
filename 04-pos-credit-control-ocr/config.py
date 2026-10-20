"""
Configuration for Real-Time POS Credit Control & OCR Bot.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

TESSERACT_PATH = os.getenv("TESSERACT_CMD_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
SCAN_INTERVAL = float(os.getenv("SCREEN_SCAN_INTERVAL", "2.0"))

TARGET_WINDOW = os.getenv("TARGET_WINDOW_TITLE", "Billing")
TENDER_MODAL = os.getenv("TENDER_MODAL_TITLE", "Tender")

# Default blacklisted / overdue credit parties to restrict
DEFAULT_OVERDUE_PARTIES = [
    "ACME SUPERMARKET",
    "GLOBAL TRADERS",
    "HORIZON MART",
    "DEBTOR CO"
]
