"""
DIP Violation Examples — LLD Chronicles #5
Three patterns showing high-level modules directly coupled to low-level details.
"""
import csv
import json
import smtplib


# ─── Violation 1: OrderService coupled to MySQLOrderRepository ───────────────

class MySQLOrderRepository:
    """
    Low-level detail: stores orders in MySQL.
    Direct instantiation couples OrderService to this specific database forever.
    """

    def __init__(self, host: str, port: int, database: str):
        self.host = host
        self.port = port
        self.database = database
        # In real code: self.connection = mysql.connector.connect(...)
        print(f"[MySQL] Connected to {host}:{port}/{database}")

    def save(self, order: dict) -> dict:
        print(f"[MySQL] INSERT INTO orders VALUES {order}")
        return {**order, "id": 1001, "status": "saved"}

    def find_by_id(self, order_id: int) -> dict:
        print(f"[MySQL] SELECT * FROM orders WHERE id = {order_id}")
        return {"id": order_id, "item": "Widget", "amount": 49.99}

    def find_by_customer(self, customer_id: int) -> list:
        print(f"[MySQL] SELECT * FROM orders WHERE customer_id = {customer_id}")
        return [{"id": 1001, "item": "Widget", "amount": 49.99}]


class OrderService:
    """
    High-level business logic. But it directly instantiates MySQLOrderRepository —
    it OWNS the low-level detail instead of depending on an abstraction.

    Consequences:
    - Can't test without a real MySQL connection
    - Can't switch to PostgreSQL without modifying this class
    - Can't add a caching layer without modifying this class
    - Every deploy of a new database version requires touching business logic
    """

    def __init__(self):
        # High-level module creates its own low-level dependency.
        # This is the DIP violation — the direction of control flows downward.
        self.repository = MySQLOrderRepository(
            host="prod-mysql-01.internal",
            port=3306,
            database="orders_db"
        )

    def place_order(self, customer_id: int, item: str, amount: float) -> dict:
        order = {"customer_id": customer_id, "item": item, "amount": amount}
        saved = self.repository.save(order)
        print(f"Order placed: {saved}")
        return saved

    def get_order(self, order_id: int) -> dict:
        return self.repository.find_by_id(order_id)

    def get_customer_orders(self, customer_id: int) -> list:
        return self.repository.find_by_customer(customer_id)


# ─── Violation 2: NotificationService coupled to concrete senders ─────────────

class SmtpEmailSender:
    """Low-level detail: sends email via SMTP."""

    def __init__(self, smtp_host: str, smtp_port: int):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        print(f"[SMTP] Connected to {smtp_host}:{smtp_port}")

    def send(self, to: str, subject: str, body: str) -> None:
        print(f"[SMTP] Sending email to {to}: {subject}")


class TwilioSmsSender:
    """Low-level detail: sends SMS via Twilio."""

    def __init__(self, account_sid: str, auth_token: str):
        self.account_sid = account_sid
        print(f"[Twilio] Auth with SID {account_sid[:8]}...")

    def send(self, to_number: str, message: str) -> None:
        print(f"[Twilio] SMS to {to_number}: {message}")


class NotificationService:
    """
    High-level notification orchestration — but hardwired to SMTP and Twilio.
    The if/elif block means every new channel (Slack, push, webhook) forces
    this class to change. And you can never test it without real credentials.
    """

    def __init__(self):
        # Both low-level senders instantiated directly inside.
        # Switching from Twilio to AWS SNS requires modifying business logic.
        self.email_sender = SmtpEmailSender(
            smtp_host="smtp.company.com",
            smtp_port=587
        )
        self.sms_sender = TwilioSmsSender(
            account_sid="ACxxxxxxxx",
            auth_token="auth_token_secret"
        )

    def notify_order_placed(self, customer: dict, order: dict) -> None:
        channel = customer.get("preferred_channel", "email")

        if channel == "email":
            self.email_sender.send(
                to=customer["email"],
                subject=f"Order #{order['id']} confirmed",
                body=f"Your order for {order['item']} is confirmed."
            )
        elif channel == "sms":
            self.sms_sender.send(
                to_number=customer["phone"],
                message=f"Order #{order['id']} confirmed: {order['item']}"
            )
        else:
            # New channel? Must modify this class.
            raise ValueError(f"Unsupported channel: {channel}")  # DIP + OCP violation


# ─── Violation 3: ReportGenerator coupled to the filesystem ──────────────────

class ReportGenerator:
    """
    High-level reporting logic — but it directly writes to the filesystem.
    Can't test without writing real files. Can't upload to S3 without modifying
    this class. Can't write to a database without modifying this class.
    The report format logic is entangled with the storage mechanism.
    """

    def generate_sales_report(self, orders: list, output_path: str) -> None:
        """Builds the report AND decides where to put it. Two responsibilities."""
        if output_path.endswith(".csv"):
            self._write_csv(orders, output_path)
        elif output_path.endswith(".json"):
            self._write_json(orders, output_path)
        else:
            raise ValueError(f"Unsupported format: {output_path}")  # DIP + OCP violation

    def _write_csv(self, orders: list, path: str) -> None:
        # Directly coupled to filesystem I/O
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "item", "amount"])
            writer.writeheader()
            writer.writerows(orders)
        print(f"[CSV] Report written to {path}")

    def _write_json(self, orders: list, path: str) -> None:
        # Directly coupled to filesystem I/O
        with open(path, "w") as f:
            json.dump({"orders": orders, "total": len(orders)}, f, indent=2)
        print(f"[JSON] Report written to {path}")


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # OrderService creates its own database — can't test without MySQL
    service = OrderService()
    order = service.place_order(customer_id=42, item="Widget", amount=49.99)

    # NotificationService creates its own senders — can't test without credentials
    notifier = NotificationService()
    notifier.notify_order_placed(
        customer={"email": "user@example.com", "preferred_channel": "email"},
        order=order
    )

    # ReportGenerator writes to disk — can't test without filesystem side effects
    reporter = ReportGenerator()
    reporter.generate_sales_report(
        orders=[{"id": 1001, "item": "Widget", "amount": 49.99}],
        output_path="sales_report.csv"
    )
