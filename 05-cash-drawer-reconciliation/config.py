"""
Configuration for Cash Drawer Reconciliation Suite.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

ERP_APP_PATH = os.getenv("ERP_APP_PATH", "")
DEFAULT_OPENING_BALANCE = float(os.getenv("DEFAULT_OPENING_BALANCE", "15000.0"))

SAMPLE_COUNTER_BALANCES = {
    "Counter 1": 18450.0,
    "Counter 2": 24320.0,
    "Counter 3": 12100.0,
    "Counter 4": 31500.0,
    "Counter 5": 8900.0
}
