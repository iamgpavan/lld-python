"""
ISP Compliant Examples — LLD Chronicles #4
Segregated interfaces: each client depends only on the methods it actually uses.
"""
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


# ─── Fix 1: Segregated Device Interfaces ─────────────────────────────────────
# Four narrow interfaces instead of one fat one.
# Implementations compose only what they genuinely support.

class Printable(ABC):
    @abstractmethod
    def print_document(self, content: str) -> None:
        pass


class Scannable(ABC):
    @abstractmethod
    def scan_document(self) -> str:
        pass


class Faxable(ABC):
    @abstractmethod
    def fax_document(self, content: str, number: str) -> None:
        pass


class Stapleable(ABC):
    @abstractmethod
    def staple_pages(self, count: int) -> None:
        pass


class BasicPrinter(Printable):
    """Only implements what it actually supports. Zero stubs."""

    def print_document(self, content: str) -> None:
        print(f"[Basic] Printing: {content}")


class AllInOnePrinter(Printable, Scannable, Faxable, Stapleable):
    """Honestly implements every interface it genuinely supports."""

    def print_document(self, content: str) -> None:
        print(f"[AllInOne] Printing: {content}")

    def scan_document(self) -> str:
        return "[AllInOne] Scanned document"

    def fax_document(self, content: str, number: str) -> None:
        print(f"[AllInOne] Faxing to {number}: {content}")

    def staple_pages(self, count: int) -> None:
        print(f"[AllInOne] Stapling {count} pages")


def print_batch(printer: Printable, docs: list) -> None:
    """
    This function only needs Printable. It cannot accidentally call
    scan_document() or fax_document() — they don't exist on the type.
    BasicPrinter and AllInOnePrinter both work here without any special cases.
    """
    for doc in docs:
        printer.print_document(doc)


def scan_and_archive(scanner: Scannable) -> str:
    """Accepts anything that can scan. BasicPrinter can't be passed here by mistake."""
    return scanner.scan_document()


# ─── Fix 2: Segregated Pipeline Worker Interfaces ────────────────────────────
# Five narrow interfaces. Each worker composes only what it needs.
# Changing send_email_report's signature no longer touches AnalyticsWorker.

class DataFetcher(ABC):
    @abstractmethod
    def fetch_data(self, source: str) -> list:
        pass


class DataProcessor(ABC):
    @abstractmethod
    def process_data(self, records: list) -> list:
        pass


class CsvExporter(ABC):
    @abstractmethod
    def export_to_csv(self, records: list, path: str) -> None:
        pass


class EmailReporter(ABC):
    @abstractmethod
    def send_email_report(self, records: list, recipient: str) -> None:
        pass


class DataArchiver(ABC):
    @abstractmethod
    def archive_old_records(self, before_date: str) -> int:
        pass


class AnalyticsWorker(DataFetcher, DataProcessor):
    """Fetches and processes. Nothing else. No stubs anywhere."""

    def fetch_data(self, source: str) -> list:
        return [{"id": 1, "value": "analytics_data"}]

    def process_data(self, records: list) -> list:
        return [{"id": r["id"], "processed": True} for r in records]


class ExportWorker(DataFetcher, CsvExporter):
    """Finance team worker: fetch + export to CSV. Clean composition."""

    def fetch_data(self, source: str) -> list:
        return [{"id": 1, "value": "export_data"}]

    def export_to_csv(self, records: list, path: str) -> None:
        print(f"Exporting {len(records)} records to {path}")


class ArchiveWorker(DataFetcher, DataArchiver):
    """DevOps worker: fetch + archive. Exactly what it does, nothing more."""

    def fetch_data(self, source: str) -> list:
        return [{"id": 1, "value": "old_record"}]

    def archive_old_records(self, before_date: str) -> int:
        print(f"Archiving records before {before_date}")
        return 17


class FullPipelineWorker(DataFetcher, DataProcessor, CsvExporter, EmailReporter, DataArchiver):
    """The full pipeline worker. Honestly implements every interface it composes."""

    def fetch_data(self, source: str) -> list:
        return [{"id": 1, "value": "full_data"}]

    def process_data(self, records: list) -> list:
        return [{"id": r["id"], "processed": True} for r in records]

    def export_to_csv(self, records: list, path: str) -> None:
        print(f"Exporting {len(records)} records to {path}")

    def send_email_report(self, records: list, recipient: str) -> None:
        print(f"Emailing report to {recipient}")

    def archive_old_records(self, before_date: str) -> int:
        print(f"Archiving records before {before_date}")
        return 42


def run_analytics_pipeline(worker: DataFetcher, processor: DataProcessor) -> list:
    """
    Type system enforces the contract. You cannot pass ArchiveWorker here
    because it doesn't implement DataProcessor — the error is at call site,
    not at runtime when process_data() raises NotImplementedError.
    """
    records = worker.fetch_data("warehouse")
    return processor.process_data(records)


# ─── Fix 3: Segregated User Service Interfaces ───────────────────────────────
# Four narrow service interfaces. AuditService depends only on UserReader.
# Changing CSV export logic is now invisible to the compliance team's service.

class UserReader(ABC):
    @abstractmethod
    def get_user(self, user_id: int) -> dict:
        pass


class UserWriter(ABC):
    @abstractmethod
    def create_user(self, data: dict) -> dict:
        pass

    @abstractmethod
    def update_user(self, user_id: int, data: dict) -> dict:
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> None:
        pass


class UserEmailer(ABC):
    @abstractmethod
    def send_welcome_email(self, user_id: int) -> None:
        pass


class UserReporter(ABC):
    @abstractmethod
    def generate_activity_report(self, user_id: int) -> dict:
        pass

    @abstractmethod
    def export_user_data_csv(self, user_id: int, path: str) -> None:
        pass


class AuditService(UserReader):
    """Read-only compliance service. Implements exactly one interface. Zero stubs."""

    def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "Pavan", "role": "admin"}


class FullUserService(UserReader, UserWriter, UserEmailer, UserReporter):
    """The main application service. Every interface it declares, it genuinely supports."""

    def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "Pavan"}

    def create_user(self, data: dict) -> dict:
        return {"id": 999, **data}

    def update_user(self, user_id: int, data: dict) -> dict:
        return {"id": user_id, **data}

    def delete_user(self, user_id: int) -> None:
        print(f"Deleted user {user_id}")

    def send_welcome_email(self, user_id: int) -> None:
        print(f"Welcome email sent to user {user_id}")

    def generate_activity_report(self, user_id: int) -> dict:
        return {"user_id": user_id, "logins": 42, "actions": 118}

    def export_user_data_csv(self, user_id: int, path: str) -> None:
        print(f"Exported user {user_id} data to {path}")


def display_user_profile(service: UserReader, user_id: int) -> None:
    """
    This view layer function only needs UserReader. Passing FullUserService
    works. Passing AuditService works. Passing anything with create_user
    by accident? The type checker stops it at the call site.
    """
    user = service.get_user(user_id)
    print(f"Profile: {user['name']} (ID: {user['id']})")


# ─── Protocol approach: structural subtyping, no inheritance at all ───────────
# ISP taken to its logical conclusion: you don't even need explicit inheritance.
# Any object that has the right method satisfies the interface.

@runtime_checkable
class PrintableProtocol(Protocol):
    def print_document(self, content: str) -> None: ...


@runtime_checkable
class ScannableProtocol(Protocol):
    def scan_document(self) -> str: ...


class NetworkPrinter:
    """
    No ABC, no inheritance. Structurally satisfies PrintableProtocol
    simply by having the right method. The Protocol is the interface;
    nothing else needs to change.
    """

    def print_document(self, content: str) -> None:
        print(f"[Network] Printing via TCP/IP: {content}")


def send_to_any_printer(printer: PrintableProtocol, content: str) -> None:
    """
    Accepts BasicPrinter (ABC), AllInOnePrinter (ABC), or NetworkPrinter
    (Protocol, no ABC at all). ISP + duck typing: the smallest possible
    interface, with the loosest possible coupling.
    """
    printer.print_document(content)


if __name__ == "__main__":
    # Device interfaces
    basic = BasicPrinter()
    aio = AllInOnePrinter()
    network = NetworkPrinter()

    print_batch(basic, ["Invoice #001", "Invoice #002"])
    print_batch(aio, ["Contract.pdf"])
    send_to_any_printer(network, "Q3 Budget Report")

    scanned = scan_and_archive(aio)
    print(f"Archived: {scanned}")

    # Pipeline workers
    analytics = AnalyticsWorker()
    result = run_analytics_pipeline(analytics, analytics)
    print(f"Analytics result: {result}")

    exporter = ExportWorker()
    exporter.export_to_csv(exporter.fetch_data("db"), "/tmp/report.csv")

    archiver = ArchiveWorker()
    count = archiver.archive_old_records("2024-01-01")
    print(f"Archived {count} records")

    # User services
    audit = AuditService()
    display_user_profile(audit, 42)

    full = FullUserService()
    display_user_profile(full, 1)
    full.send_welcome_email(1)
