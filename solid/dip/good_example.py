"""
DIP Compliant Examples — LLD Chronicles #5
Inverted dependencies: high-level modules depend on abstractions, not details.
Details are injected — never created inside business logic.
"""
import csv
import io
import json
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


# ─── Fix 1: OrderService depends on OrderRepository abstraction ───────────────

class OrderRepository(ABC):
    """
    The abstraction that both the high-level module (OrderService) and the
    low-level details (MySQLOrderRepository, PostgresOrderRepository) depend on.
    This is the 'inversion': the dependency arrow now points UP, toward the
    abstraction, instead of down toward the concrete implementation.
    """

    @abstractmethod
    def save(self, order: dict) -> dict:
        pass

    @abstractmethod
    def find_by_id(self, order_id: int) -> dict:
        pass

    @abstractmethod
    def find_by_customer(self, customer_id: int) -> list:
        pass


class MySQLOrderRepository(OrderRepository):
    """Low-level detail. Depends on the abstraction (inherits from it)."""

    def __init__(self, host: str, port: int, database: str):
        self.host = host
        self.port = port
        self.database = database
        print(f"[MySQL] Connected to {host}:{port}/{database}")

    def save(self, order: dict) -> dict:
        print(f"[MySQL] INSERT INTO orders: {order}")
        return {**order, "id": 1001, "status": "saved"}

    def find_by_id(self, order_id: int) -> dict:
        print(f"[MySQL] SELECT * FROM orders WHERE id = {order_id}")
        return {"id": order_id, "item": "Widget", "amount": 49.99}

    def find_by_customer(self, customer_id: int) -> list:
        print(f"[MySQL] SELECT * FROM orders WHERE customer_id = {customer_id}")
        return [{"id": 1001, "item": "Widget", "amount": 49.99}]


class PostgresOrderRepository(OrderRepository):
    """Swap in without touching OrderService."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        print(f"[Postgres] Connected via DSN")

    def save(self, order: dict) -> dict:
        print(f"[Postgres] INSERT INTO orders: {order}")
        return {**order, "id": 2001, "status": "saved"}

    def find_by_id(self, order_id: int) -> dict:
        print(f"[Postgres] SELECT * FROM orders WHERE id = {order_id}")
        return {"id": order_id, "item": "Widget", "amount": 49.99}

    def find_by_customer(self, customer_id: int) -> list:
        print(f"[Postgres] SELECT * FROM orders WHERE customer_id = {customer_id}")
        return [{"id": 2001, "item": "Widget", "amount": 49.99}]


class InMemoryOrderRepository(OrderRepository):
    """
    Test double. No database, no network, no credentials.
    Injected in tests — OrderService has no idea it's not MySQL.
    This is the DIP testing superpower.
    """

    def __init__(self):
        self._store: dict[int, dict] = {}
        self._next_id = 1

    def save(self, order: dict) -> dict:
        saved = {**order, "id": self._next_id, "status": "saved"}
        self._store[self._next_id] = saved
        self._next_id += 1
        return saved

    def find_by_id(self, order_id: int) -> dict:
        return self._store.get(order_id, {})

    def find_by_customer(self, customer_id: int) -> list:
        return [o for o in self._store.values() if o.get("customer_id") == customer_id]


class OrderService:
    """
    High-level business logic. Depends only on OrderRepository (the abstraction).
    The concrete repository is INJECTED — OrderService never creates it.
    Switching databases = change one line at the composition root. That's it.
    """

    def __init__(self, repository: OrderRepository):
        # The dependency is received, not created.
        # The direction has inverted: both this class and the repository
        # now point toward the abstraction, not toward each other.
        self.repository = repository

    def place_order(self, customer_id: int, item: str, amount: float) -> dict:
        order = {"customer_id": customer_id, "item": item, "amount": amount}
        saved = self.repository.save(order)
        print(f"Order placed: {saved}")
        return saved

    def get_order(self, order_id: int) -> dict:
        return self.repository.find_by_id(order_id)

    def get_customer_orders(self, customer_id: int) -> list:
        return self.repository.find_by_customer(customer_id)


# ─── Fix 2: NotificationService depends on NotificationSender abstraction ─────

class NotificationSender(ABC):
    """The abstraction. High-level NotificationService depends on this."""

    @abstractmethod
    def send(self, recipient: str, subject: str, body: str) -> None:
        pass


class SmtpEmailSender(NotificationSender):
    def __init__(self, smtp_host: str, smtp_port: int):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send(self, recipient: str, subject: str, body: str) -> None:
        print(f"[SMTP] Email to {recipient}: {subject}")


class TwilioSmsSender(NotificationSender):
    def __init__(self, account_sid: str, auth_token: str):
        self.account_sid = account_sid

    def send(self, recipient: str, subject: str, body: str) -> None:
        print(f"[Twilio] SMS to {recipient}: {body[:80]}")


class SlackSender(NotificationSender):
    """New channel. Zero changes to NotificationService."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, recipient: str, subject: str, body: str) -> None:
        print(f"[Slack] Post to #{recipient}: {subject} — {body[:60]}")


class SilentSender(NotificationSender):
    """Test double. Captures sent messages for assertion without side effects."""

    def __init__(self):
        self.sent: list[dict] = []

    def send(self, recipient: str, subject: str, body: str) -> None:
        self.sent.append({"recipient": recipient, "subject": subject, "body": body})


class NotificationService:
    """
    High-level notification logic. Depends only on NotificationSender.
    No if/elif. No channel-switching logic. No credentials.
    Adding Slack, push notifications, or webhooks = new class only.
    """

    def __init__(self, sender: NotificationSender):
        self.sender = sender

    def notify_order_placed(self, recipient: str, order: dict) -> None:
        self.sender.send(
            recipient=recipient,
            subject=f"Order #{order['id']} confirmed",
            body=f"Your order for {order['item']} (${order['amount']:.2f}) is confirmed."
        )

    def notify_order_shipped(self, recipient: str, order: dict, tracking: str) -> None:
        self.sender.send(
            recipient=recipient,
            subject=f"Order #{order['id']} shipped",
            body=f"Tracking number: {tracking}"
        )


# ─── Fix 3: ReportGenerator depends on DataWriter abstraction ─────────────────

class DataWriter(ABC):
    """The abstraction for where data goes. ReportGenerator depends on this."""

    @abstractmethod
    def write(self, content: str) -> None:
        pass

    @abstractmethod
    def get_result(self) -> str:
        pass


class CsvFileWriter(DataWriter):
    """Writes to a local file."""

    def __init__(self, path: str):
        self.path = path
        self._content = ""

    def write(self, content: str) -> None:
        with open(self.path, "w") as f:
            f.write(content)
        self._content = content
        print(f"[File] Written to {self.path}")

    def get_result(self) -> str:
        return self.path


class InMemoryWriter(DataWriter):
    """Test double. No filesystem, no cleanup, fully inspectable in tests."""

    def __init__(self):
        self._buffer = io.StringIO()

    def write(self, content: str) -> None:
        self._buffer = io.StringIO(content)

    def get_result(self) -> str:
        return self._buffer.getvalue()


class S3Writer(DataWriter):
    """Writes to S3. New destination — zero changes to ReportGenerator."""

    def __init__(self, bucket: str, key: str):
        self.bucket = bucket
        self.key = key
        self._uploaded = ""

    def write(self, content: str) -> None:
        # boto3.client("s3").put_object(Bucket=self.bucket, Key=self.key, Body=content)
        self._uploaded = content
        print(f"[S3] Uploaded to s3://{self.bucket}/{self.key}")

    def get_result(self) -> str:
        return f"s3://{self.bucket}/{self.key}"


class ReportGenerator:
    """
    High-level report formatting logic. Knows how to build the report.
    Has no idea where the result goes — that's the writer's job.
    Format logic and storage are now separate, testable, swappable.
    """

    def __init__(self, writer: DataWriter):
        self.writer = writer

    def generate_sales_report(self, orders: list) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["id", "item", "amount"])
        writer.writeheader()
        writer.writerows(orders)
        self.writer.write(output.getvalue())
        return self.writer.get_result()

    def generate_summary_report(self, orders: list) -> str:
        total = sum(o["amount"] for o in orders)
        summary = {"total_orders": len(orders), "total_revenue": total, "orders": orders}
        self.writer.write(json.dumps(summary, indent=2))
        return self.writer.get_result()


# ─── Protocol approach: structural DIP without ABC ────────────────────────────

@runtime_checkable
class OrderStore(Protocol):
    def save(self, order: dict) -> dict: ...
    def find_by_id(self, order_id: int) -> dict: ...
    def find_by_customer(self, customer_id: int) -> list: ...


class DictOrderStore:
    """
    Satisfies OrderStore structurally — no inheritance.
    A simple dict-backed store for integration tests or local dev.
    """

    def __init__(self):
        self._data: dict[int, dict] = {}
        self._seq = 1

    def save(self, order: dict) -> dict:
        saved = {**order, "id": self._seq}
        self._data[self._seq] = saved
        self._seq += 1
        return saved

    def find_by_id(self, order_id: int) -> dict:
        return self._data.get(order_id, {})

    def find_by_customer(self, customer_id: int) -> list:
        return [o for o in self._data.values() if o.get("customer_id") == customer_id]


# ─── Composition root — wires it all together ─────────────────────────────────
# This is the ONLY place that knows which concrete implementations to use.
# Change database: edit one line here. Business logic never changes.

def create_production_stack():
    repository = MySQLOrderRepository(
        host="prod-mysql-01.internal",
        port=3306,
        database="orders_db"
    )
    sender = SmtpEmailSender(smtp_host="smtp.company.com", smtp_port=587)
    writer = CsvFileWriter(path="/reports/sales.csv")

    order_service = OrderService(repository=repository)
    notifier = NotificationService(sender=sender)
    reporter = ReportGenerator(writer=writer)

    return order_service, notifier, reporter


def create_test_stack():
    """
    No real databases. No real credentials. No real files.
    All business logic is fully testable in complete isolation.
    """
    repository = InMemoryOrderRepository()
    sender = SilentSender()
    writer = InMemoryWriter()

    order_service = OrderService(repository=repository)
    notifier = NotificationService(sender=sender)
    reporter = ReportGenerator(writer=writer)

    return order_service, notifier, reporter, sender


if __name__ == "__main__":
    # Test stack — no infrastructure needed
    order_service, notifier, reporter, silent_sender = create_test_stack()

    order = order_service.place_order(customer_id=42, item="Widget", amount=49.99)
    print(f"Placed: {order}")

    notifier.notify_order_placed(recipient="user@example.com", order=order)
    print(f"Notifications sent: {len(silent_sender.sent)}")
    print(f"Last notification: {silent_sender.sent[-1]['subject']}")

    result_path = reporter.generate_sales_report(orders=[order])
    print(f"Report content:\n{reporter.writer.get_result()}")

    # Swap to Slack — zero changes to business logic
    slack_notifier = NotificationService(sender=SlackSender(webhook_url="https://hooks.slack.com/..."))
    slack_notifier.notify_order_placed(recipient="orders-channel", order=order)
