"""
Configuration and Database Abstraction Layer for Damage Claims Portal.
Supports both SQLite (for zero-setup standalone running) and MS SQL Server (production).
"""
import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
SQLITE_PATH = Path(os.getenv("SQLITE_DB_PATH", str(BASE_DIR / "damage_portal.db")))

SQL_SERVER_HOST = os.getenv("SQL_SERVER_HOST", "localhost")
SQL_SERVER_DB = os.getenv("SQL_SERVER_DB", "DAMAGE")
SQL_SERVER_USER = os.getenv("SQL_SERVER_USER", "sa")
SQL_SERVER_PASSWORD = os.getenv("SQL_SERVER_PASSWORD", "")

def get_connection():
    """Returns an active DB connection and cursor wrapper."""
    if DB_ENGINE == "sqlserver":
        import pyodbc
        conn_str = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={SQL_SERVER_HOST};"
            f"DATABASE={SQL_SERVER_DB};"
            f"UID={SQL_SERVER_USER};"
            f"PWD={SQL_SERVER_PASSWORD};"
        )
        return pyodbc.connect(conn_str)
    else:
        init_sqlite_if_needed()
        return sqlite3.connect(SQLITE_PATH)

def init_sqlite_if_needed():
    """Initializes SQLite database with schema if not yet present."""
    if not SQLITE_PATH.exists():
        conn = sqlite3.connect(SQLITE_PATH)
        schema_file = BASE_DIR / "database_schema.sql"
        if schema_file.exists():
            with open(schema_file, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
        conn.commit()
        conn.close()
        print(f"[+] Initialized standalone SQLite database at {SQLITE_PATH}")
