"""
Credit Guard OCR: Real-Time POS Screen Monitoring & Keystroke Interceptor
Continuously captures retail billing screens, applies Tesseract OCR, detects overdue/restricted
customer accounts, and intercepts cashier input to prevent unauthorized credit invoicing.
"""
import time
import pyautogui
import pytesseract
import pygetwindow as gw
import keyboard
import config

# Setup Tesseract binary path
if hasattr(pytesseract, "pytesseract") and hasattr(config, "TESSERACT_PATH"):
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

class POSCreditGuard:
    def __init__(self, overdue_parties=None):
        self.overdue_parties = overdue_parties or config.DEFAULT_OVERDUE_PARTIES
        self.is_locked = False
        print("[*] POS Credit Guard Active.")
        print(f"[*] Restricted Debtors Monitored: {', '.join(self.overdue_parties)}")

    def is_pos_active(self) -> bool:
        """Checks if any target POS or billing window is currently active."""
        active_win = gw.getActiveWindow()
        if active_win:
            title = active_win.title.lower()
            return config.TARGET_WINDOW.lower() in title or config.TENDER_MODAL.lower() in title
        return True

    def scan_screen(self):
        """Captures screen and checks for debtor name presence via OCR."""
        screenshot = pyautogui.screenshot()
        try:
            detected_text = pytesseract.image_to_string(screenshot)
        except Exception as e:
            print(f"[-] OCR extraction failed (Is Tesseract installed?): {e}")
            return None

        for party in self.overdue_parties:
            if party.lower() in detected_text.lower():
                return party
        return None

    def trigger_lockdown(self, detected_party: str):
        """Blocks key inputs to prevent cashier from finalizing the checkout."""
        if self.is_locked:
            return

        self.is_locked = True
        print(f"\n[ALERT] Overdue debtor '{detected_party}' detected on billing screen!")
        print("[!] RESTRICTING CHECKOUT KEYSTROKES: Enter, numeric keys disabled.")
        print("[!] Press 'Ctrl + Shift + Q' to unlock.")

        # Intercept critical payment confirmation keys
        keyboard.block_key('enter')
        for digit in range(10):
            keyboard.block_key(str(digit))

        keyboard.add_hotkey('ctrl+shift+q', self.release_lockdown)

    def release_lockdown(self):
        """Unblocks all hooked key events."""
        if self.is_locked:
            keyboard.unhook_all()
            self.is_locked = False
            print("[+] Checkout keys restored.")

    def run_monitor(self):
        """Main continuous background scanning loop."""
        print("[*] Monitoring screen every", config.SCAN_INTERVAL, "seconds. Press Ctrl+C to terminate.")
        try:
            while True:
                if self.is_pos_active():
                    match = self.scan_screen()
                    if match:
                        self.trigger_lockdown(match)
                time.sleep(config.SCAN_INTERVAL)
        except KeyboardInterrupt:
            self.release_lockdown()
            print("\n[*] Monitor terminated.")

if __name__ == "__main__":
    guard = POSCreditGuard()
    guard.run_monitor()
