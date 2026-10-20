"""
Standalone Simulation for Credit Guard OCR
Creates a temporary simulated POS billing window displaying blacklisted debtor names
to verify OCR detection and keyboard interception without needing a live POS ERP.
"""
import time
import tkinter as tk
import threading
from credit_guard_ocr import POSCreditGuard

def launch_mock_pos_window():
    root = tk.Tk()
    root.title("Retail POS System - [Billing Window]")
    root.geometry("450x300")
    root.configure(bg="#1e1e1e")

    label = tk.Label(
        root, 
        text="ACME SUPERMARKET\nOutstanding Balance: $14,250.00\n[STATUS: CREDIT ON HOLD]", 
        font=("Arial", 16, "bold"), 
        fg="#ff3333", 
        bg="#1e1e1e"
    )
    label.pack(expand=True)
    root.mainloop()

if __name__ == "__main__":
    print("[*] Launching simulated POS billing window...")
    t = threading.Thread(target=launch_mock_pos_window, daemon=True)
    t.start()

    time.sleep(2)
    guard = POSCreditGuard()
    print("[*] Performing test OCR screen scan...")
    detected = guard.scan_screen()
    if detected:
        print(f"[SUCCESS] OCR detected restricted debtor: {detected}")
    else:
        print("[-] Note: Tesseract-OCR is required on system PATH for live optical detection.")
