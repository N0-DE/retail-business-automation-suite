"""
Biometric Sync Service
Queries MS SQL Server biometric attendance backend (eTimeTrackLite)
or generates clean standardized CSV logs from raw punch records.
"""
import pandas as pd
import config

def sync_biometric_data(target_date: str = None):
    """
    Pulls punch in/out timestamps from biometric SQL database or falls back to mock data.
    """
    if config.USE_MOCK_DATA:
        print("[*] Mock Mode Enabled: Loading sample biometric attendance dataset...")
        df = pd.read_csv(config.DEFAULT_ATTENDANCE_FILE)
        output_csv = config.EXPORT_DIR / "attendance_synced.csv"
        df.to_csv(output_csv, index=False)
        print(f"[+] Attendance dataset staged at {output_csv}")
        return df

    try:
        import pyodbc
        conn_str = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={config.DB_SERVER};"
            f"DATABASE={config.DB_NAME};"
            f"UID={config.DB_USER};"
            f"PWD={config.DB_PASSWORD};"
        )
        conn = pyodbc.connect(conn_str)
        query = """
        SELECT 
            Employees.EmployeeCode,
            Employees.EmployeeName,
            AttendanceLogs.InTime, 
            AttendanceLogs.OutTime, 
            AttendanceLogs.PunchRecords,
            AttendanceLogs.AttendanceDate
        FROM AttendanceLogs
        INNER JOIN Employees ON AttendanceLogs.EmployeeId = Employees.EmployeeId
        ORDER BY AttendanceLogs.AttendanceDate DESC, Employees.EmployeeCode;
        """
        df = pd.read_sql(query, conn)
        conn.close()

        output_csv = config.EXPORT_DIR / "attendance_synced.csv"
        df.to_csv(output_csv, index=False)
        print(f"[+] Successfully fetched {len(df)} records from biometric SQL Server.")
        return df
    except Exception as e:
        print(f"[-] Database query failed: {e}. Falling back to sample data.")
        return pd.read_csv(config.DEFAULT_ATTENDANCE_FILE)

if __name__ == "__main__":
    sync_biometric_data()
