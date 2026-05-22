"""
SRP Applied: One class, one reason to change.
Each class owns exactly one responsibility. Swapping the email provider
or DB engine touches exactly one file — not everything.
"""

import sqlite3
import smtplib
import logging
import re
from datetime import datetime


# ── 1. UserValidator — knows what makes a valid user ───────────────────────

class UserValidator:
    def validate_email(self, email: str) -> bool:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(pattern, email))

    def validate_password(self, password: str) -> bool:
        if len(password) < 8:
            return False
        if not any(c.isupper() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        return True


# ── 2. UserRepository — knows how to persist users ─────────────────────────

class UserRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def save(self, user: dict) -> int:
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

    def update(self, user_id: int, data: dict) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        fields = ", ".join(f"{k} = ?" for k in data)
        values = list(data.values()) + [user_id]
        cursor.execute(f"UPDATE users SET {fields} WHERE id = ?", values)
        conn.commit()
        conn.close()

    def find_by_id(self, user_id: int) -> dict | None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"id": row[0], "name": row[1], "email": row[2]}
        return None


# ── 3. EmailService — knows how to deliver emails ──────────────────────────

class EmailService:
    def __init__(self, smtp_host: str, smtp_port: int):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send_welcome(self, user: dict) -> None:
        self._send(
            to=user["email"],
            subject="Welcome aboard!",
            body=f"Hi {user['name']}, thanks for joining us.",
        )

    def send_password_reset(self, user: dict, reset_token: str) -> None:
        self._send(
            to=user["email"],
            subject="Reset your password",
            body=f"Hi {user['name']}, your reset token: {reset_token}",
        )

    def _send(self, to: str, subject: str, body: str) -> None:
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.sendmail("noreply@app.com", to, f"Subject: {subject}\n\n{body}")


# ── 4. UserLogger — knows how to record activity ───────────────────────────

class UserLogger:
    def __init__(self):
        self._log = logging.getLogger(__name__)

    def info(self, user_id: int, action: str) -> None:
        self._log.info(
            "[%s] User %d: %s", datetime.utcnow().isoformat(), user_id, action
        )

    def error(self, user_id: int, message: str) -> None:
        self._log.error("User %d error: %s", user_id, message)


# ── 5. ReportService — knows how to build user reports ─────────────────────

class ReportService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def generate_user_report(self, user_id: int) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        cursor.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,)
        )
        order_count = cursor.fetchone()[0]
        conn.close()
        return {
            "user_id": user_id,
            "name": row[0],
            "email": row[1],
            "total_orders": order_count,
            "report_generated_at": datetime.utcnow().isoformat(),
        }


# ── 6. UserService — thin orchestrator, owns the workflow ──────────────────

class UserService:
    def __init__(
        self,
        validator: UserValidator,
        repository: UserRepository,
        email_service: EmailService,
        logger: UserLogger,
    ):
        self.validator = validator
        self.repository = repository
        self.email_service = email_service
        self.logger = logger

    def register(self, user: dict) -> int:
        if not self.validator.validate_email(user["email"]):
            raise ValueError(f"Invalid email: {user['email']}")

        user_id = self.repository.save(user)
        self.email_service.send_welcome(user)
        self.logger.info(user_id, "registered")
        return user_id


# ── Demo ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    DB = "app.db"
    SMTP_HOST = "smtp.example.com"
    SMTP_PORT = 587

    service = UserService(
        validator=UserValidator(),
        repository=UserRepository(DB),
        email_service=EmailService(SMTP_HOST, SMTP_PORT),
        logger=UserLogger(),
    )

    # Swap email provider? Touch only EmailService.
    # Change DB? Touch only UserRepository.
    # Add a new validation rule? Touch only UserValidator.
    user_id = service.register({"name": "Alex", "email": "alex@example.com"})

    report_svc = ReportService(DB)
    print(report_svc.generate_user_report(user_id))
