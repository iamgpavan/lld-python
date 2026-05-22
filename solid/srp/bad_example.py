"""
SRP Violation: The God-Class
UserManager does too much — DB, email, reports, logging, and validation
all live in one class. Any change to any responsibility forces a touch here.
"""

import sqlite3
import smtplib
import logging
import re
from datetime import datetime


class UserManager:
    """
    A class that does everything user-related.
    Looks convenient at first. Becomes a nightmare at scale.
    """

    def __init__(self, db_path: str, smtp_host: str, smtp_port: int):
        self.db_path = db_path
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.logger = logging.getLogger(__name__)

    # ── Responsibility 1: Database operations ──────────────────────────────

    def save_user(self, user: dict) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)",
            (user["name"], user["email"], datetime.utcnow().isoformat()),
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id

    def update_user(self, user_id: int, data: dict) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        fields = ", ".join(f"{k} = ?" for k in data)
        values = list(data.values()) + [user_id]
        cursor.execute(f"UPDATE users SET {fields} WHERE id = ?", values)
        conn.commit()
        conn.close()

    # ── Responsibility 2: Email sending ────────────────────────────────────

    def send_welcome_email(self, user: dict) -> None:
        subject = "Welcome aboard!"
        body = f"Hi {user['name']}, thanks for joining us."
        self._send_email(user["email"], subject, body)

    def send_password_reset_email(self, user: dict, reset_token: str) -> None:
        subject = "Reset your password"
        body = f"Hi {user['name']}, use this token to reset: {reset_token}"
        self._send_email(user["email"], subject, body)

    def _send_email(self, to: str, subject: str, body: str) -> None:
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail("noreply@app.com", to, message)

    # ── Responsibility 3: Report generation ────────────────────────────────

    def generate_user_report(self, user_id: int) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        cursor.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,)
        )
        order_count = cursor.fetchone()[0]
        conn.close()
        return {
            "user_id": user_id,
            "name": row[1],
            "email": row[2],
            "total_orders": order_count,
            "report_generated_at": datetime.utcnow().isoformat(),
        }

    # ── Responsibility 4: Logging ───────────────────────────────────────────

    def log_activity(self, user_id: int, action: str) -> None:
        timestamp = datetime.utcnow().isoformat()
        self.logger.info("[%s] User %d performed: %s", timestamp, user_id, action)

    def log_error(self, user_id: int, error: str) -> None:
        self.logger.error("User %d error: %s", user_id, error)

    # ── Responsibility 5: Validation ───────────────────────────────────────

    def validate_email(self, email: str) -> bool:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(pattern, email))

    def validate_password(self, password: str) -> bool:
        # must be 8+ chars, one uppercase, one digit
        if len(password) < 8:
            return False
        if not any(c.isupper() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        return True


# ── Demo ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    manager = UserManager(
        db_path="app.db",
        smtp_host="smtp.example.com",
        smtp_port=587,
    )

    user = {"name": "Alex", "email": "alex@example.com"}

    # One class. Five jobs. Every change touches this file.
    if manager.validate_email(user["email"]):
        user_id = manager.save_user(user)
        manager.send_welcome_email(user)
        manager.log_activity(user_id, "registered")
        report = manager.generate_user_report(user_id)
        print(report)
