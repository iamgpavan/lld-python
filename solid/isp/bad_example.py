"""
ISP Violation Examples — LLD Chronicles #4
Three patterns showing how fat interfaces force unrelated dependencies.
"""
from abc import ABC, abstractmethod


# ─── Violation 1: Fat Device Interface ───────────────────────────────────────

class OfficeDevice(ABC):
    """
    One interface to rule them all. Every device must implement every capability,
    even capabilities that make no physical or logical sense for that device.
    """

    @abstractmethod
    def print_document(self, content: str) -> None:
        pass

    @abstractmethod
    def scan_document(self) -> str:
        pass

    @abstractmethod
    def fax_document(self, content: str, number: str) -> None:
        pass

    @abstractmethod
    def staple_pages(self, count: int) -> None:
        pass


class AllInOnePrinter(OfficeDevice):
    """Full-featured office machine — implements everything legitimately."""

    def print_document(self, content: str) -> None:
        print(f"[AllInOne] Printing: {content}")

    def scan_document(self) -> str:
        return "[AllInOne] Scanned document"

    def fax_document(self, content: str, number: str) -> None:
        print(f"[AllInOne] Faxing to {number}: {content}")

    def staple_pages(self, count: int) -> None:
        print(f"[AllInOne] Stapling {count} pages")


class BasicPrinter(OfficeDevice):
    """
    A simple desk printer. Only prints. But the fat OfficeDevice interface
    forces it to implement scan, fax, and staple — all of which it cannot do.
    Every caller that uses OfficeDevice must now guard against these raises.
    """

    def print_document(self, content: str) -> None:
        print(f"[Basic] Printing: {content}")

    def scan_document(self) -> str:
        raise NotImplementedError("BasicPrinter cannot scan")    # ISP violation

    def fax_document(self, content: str, number: str) -> None:
        raise NotImplementedError("BasicPrinter cannot fax")     # ISP violation

    def staple_pages(self, count: int) -> None:
        raise NotImplementedError("BasicPrinter cannot staple")  # ISP violation


# ─── Violation 2: Fat Pipeline Worker Interface ───────────────────────────────

class PipelineWorker(ABC):
    """
    Monolithic worker interface for a data platform. Every worker — whether it
    fetches, processes, exports, emails, or archives — must satisfy all five
    abstract methods. Changing any one method signature forces every worker to
    recompile, even workers that never use that method.
    """

    @abstractmethod
    def fetch_data(self, source: str) -> list:
        pass

    @abstractmethod
    def process_data(self, records: list) -> list:
        pass

    @abstractmethod
    def export_to_csv(self, records: list, path: str) -> None:
        pass

    @abstractmethod
    def send_email_report(self, records: list, recipient: str) -> None:
        pass

    @abstractmethod
    def archive_old_records(self, before_date: str) -> int:
        pass


class FullPipelineWorker(PipelineWorker):
    """The only worker that actually needs all five methods."""

    def fetch_data(self, source: str) -> list:
        return [{"id": 1, "value": "sample"}]

    def process_data(self, records: list) -> list:
        return [{"id": r["id"], "value": r["value"].upper()} for r in records]

    def export_to_csv(self, records: list, path: str) -> None:
        print(f"Exporting {len(records)} records to {path}")

    def send_email_report(self, records: list, recipient: str) -> None:
        print(f"Emailing report to {recipient}")

    def archive_old_records(self, before_date: str) -> int:
        print(f"Archiving records before {before_date}")
        return 42


class AnalyticsWorker(PipelineWorker):
    """
    Analytics team worker — only fetches and processes data.
    Forced to stub three methods it was never designed for.
    When send_email_report's signature changes, this class must be touched.
    """

    def fetch_data(self, source: str) -> list:
        return [{"id": 1, "value": "analytics_data"}]

    def process_data(self, records: list) -> list:
        return [{"id": r["id"], "processed": True} for r in records]

    def export_to_csv(self, records: list, path: str) -> None:
        raise NotImplementedError("AnalyticsWorker does not export")   # ISP violation

    def send_email_report(self, records: list, recipient: str) -> None:
        raise NotImplementedError("AnalyticsWorker does not email")    # ISP violation

    def archive_old_records(self, before_date: str) -> int:
        raise NotImplementedError("AnalyticsWorker does not archive")  # ISP violation


class ArchiveWorker(PipelineWorker):
    """
    DevOps archival worker — only needs fetch + archive.
    Must stub process, export, and email just to satisfy the contract.
    """

    def fetch_data(self, source: str) -> list:
        return [{"id": 1, "value": "old_record"}]

    def process_data(self, records: list) -> list:
        raise NotImplementedError("ArchiveWorker does not process")    # ISP violation

    def export_to_csv(self, records: list, path: str) -> None:
        raise NotImplementedError("ArchiveWorker does not export")     # ISP violation

    def send_email_report(self, records: list, recipient: str) -> None:
        raise NotImplementedError("ArchiveWorker does not email")      # ISP violation

    def archive_old_records(self, before_date: str) -> int:
        print(f"Archiving records before {before_date}")
        return 17


# ─── Violation 3: God-Service Interface ───────────────────────────────────────

class UserService(ABC):
    """
    A service interface that grew without discipline over 18 months.
    Started with get_user/create_user. Then email was added. Then reporting.
    Then CSV export. Every consumer of UserService now depends on all seven
    methods — even if it only calls one.
    """

    @abstractmethod
    def get_user(self, user_id: int) -> dict:
        pass

    @abstractmethod
    def create_user(self, data: dict) -> dict:
        pass

    @abstractmethod
    def update_user(self, user_id: int, data: dict) -> dict:
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> None:
        pass

    @abstractmethod
    def send_welcome_email(self, user_id: int) -> None:
        pass

    @abstractmethod
    def generate_activity_report(self, user_id: int) -> dict:
        pass

    @abstractmethod
    def export_user_data_csv(self, user_id: int, path: str) -> None:
        pass


class FullUserService(UserService):
    """The main application service. Legitimately implements everything."""

    def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "Pavan", "role": "admin"}

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


class AuditService(UserService):
    """
    Compliance audit service — only ever reads users.
    Forced to implement six other methods as dead stubs.
    Priya's compliance service broke in production because she had to
    implement send_welcome_email just to satisfy the interface — and
    her stub raised the wrong exception type.
    """

    def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "Pavan", "role": "admin"}

    def create_user(self, data: dict) -> dict:
        raise NotImplementedError("AuditService is read-only")         # ISP violation

    def update_user(self, user_id: int, data: dict) -> dict:
        raise NotImplementedError("AuditService is read-only")         # ISP violation

    def delete_user(self, user_id: int) -> None:
        raise NotImplementedError("AuditService is read-only")         # ISP violation

    def send_welcome_email(self, user_id: int) -> None:
        raise NotImplementedError("AuditService does not send emails") # ISP violation

    def generate_activity_report(self, user_id: int) -> dict:
        raise NotImplementedError("AuditService does not report")      # ISP violation

    def export_user_data_csv(self, user_id: int, path: str) -> None:
        raise NotImplementedError("AuditService does not export")      # ISP violation
