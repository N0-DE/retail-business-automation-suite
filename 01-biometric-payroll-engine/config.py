"""
Configuration module for Biometric Payroll Engine.
Loads settings from environment variables with sensible defaults for local development.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_SERVER = os.getenv("BIOMETRIC_DB_SERVER", "localhost")
DB_NAME = os.getenv("BIOMETRIC_DB_NAME", "etimetracklite1")
DB_USER = os.getenv("BIOMETRIC_DB_USER", "sa")
DB_PASSWORD = os.getenv("BIOMETRIC_DB_PASSWORD", "")

USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
EXPORT_DIR = Path(os.getenv("EXPORT_DIRECTORY", str(BASE_DIR / "exports")))
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_ATTENDANCE_FILE = Path(os.getenv("ATTENDANCE_LOG_PATH", str(BASE_DIR / "sample_data" / "sample_attendance.csv")))

# Hourly baseline rates (sanitized placeholder dictionary)
DEFAULT_HOURLY_RATES = {
    "ALEX JOHNSON": 75.0,
    "BRIAN SMITH": 80.0,
    "CHARLES DAVIS": 65.0,
    "DAVID MILLER": 70.0,
    "EMMA WILSON": 60.0,
    "FRANK THOMAS": 60.0,
    "GRACE TAYLOR": 65.0
}

# Designated loading team members sharing loading charge splits
DEFAULT_LOADERS = ["ALEX JOHNSON", "BRIAN SMITH", "CHARLES DAVIS"]
