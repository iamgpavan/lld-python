"""
LSP Applied: Subclasses that honour their parent's behavioural contract.

Three fixes shown:
  1. FreeTrialPayment returns 0.0 — never raises, always substitutable
  2. Square is its own class — no broken inheritance from Rectangle
  3. FileStorage split into ReadableStorage / WritableStorage so
     read-only objects never inherit a write contract they can't fulfil
"""

from abc import ABC, abstractmethod


# ══════════════════════════════════════════════════════════════════════════
# Fix 1 — FreeTrialPayment honours the contract
# ══════════════════════════════════════════════════════════════════════════

class PaymentMethod(ABC):
    @abstractmethod
    def process(self, amount: float) -> bool: ...

    @abstractmethod
    def get_fee(self, amount: float) -> float: ...

    @property
    @abstractmethod
    def name(self) -> str: ...


class CreditCardPayment(PaymentMethod):
    def process(self, amount: float) -> bool:
        print(f"Charging ${amount} to credit card")
        return True

    def get_fee(self, amount: float) -> float:
        return round(amount * 0.02, 2)

    @property
    def name(self) -> str:
        return "Credit Card"


class FreeTrialPayment(PaymentMethod):
    """
    Correct: get_fee() returns 0.0. Never raises.
    PaymentProcessor can call it without any special-case logic.
    Substitution works perfectly.
    """

    def process(self, amount: float) -> bool:
        print(f"Free trial — logging ${amount}, no charge applied")
        return True

    def get_fee(self, amount: float) -> float:
        return 0.0   # valid float, contract honoured

    @property
    def name(self) -> str:
        return "Free Trial"


class PaymentProcessor:
    """Zero knowledge of FreeTrialPayment specifically. Works for all."""

    def process_payment(self, method: PaymentMethod, amount: float) -> dict:
        fee = method.get_fee(amount)      # safe for every PaymentMethod
        total = round(amount + fee, 2)
        success = method.process(total)
        return {"success": success, "amount": amount, "fee": fee, "total": total}


# ══════════════════════════════════════════════════════════════════════════
# Fix 2 — Shape hierarchy without the Rectangle/Square trap
# Square is its own class. No broken inheritance.
# ══════════════════════════════════════════════════════════════════════════

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def set_width(self, w: float) -> None:
        self.width = w

    def set_height(self, h: float) -> None:
        self.height = h

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Square(Shape):
    """
    Square is a Shape, not a Rectangle.
    It has its own contract: one side, always equal dimensions.
    No inherited setters to break.
    """

    def __init__(self, side: float):
        self.side = side

    def set_side(self, s: float) -> None:
        self.side = s

    def area(self) -> float:
        return self.side ** 2

    def perimeter(self) -> float:
        return 4 * self.side


def print_shape_info(shape: Shape) -> None:
    """Works for any Shape — Rectangle, Square, Circle, whatever."""
    print(f"Area: {shape.area()}, Perimeter: {shape.perimeter()}")


# ══════════════════════════════════════════════════════════════════════════
# Fix 3 — Split the storage hierarchy at the capability boundary
# Code that needs write access asks for WritableStorage.
# Code that only reads accepts ReadableStorage.
# ReadOnlyStorage satisfies ReadableStorage honestly.
# ══════════════════════════════════════════════════════════════════════════

class ReadableStorage(ABC):
    @abstractmethod
    def read(self, path: str) -> bytes: ...


class WritableStorage(ReadableStorage):
    @abstractmethod
    def write(self, path: str, data: bytes) -> None: ...

    @abstractmethod
    def delete(self, path: str) -> None: ...


class LocalFileStorage(WritableStorage):
    """Full read-write storage."""

    def read(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def write(self, path: str, data: bytes) -> None:
        with open(path, "wb") as f:
            f.write(data)

    def delete(self, path: str) -> None:
        import os
        os.remove(path)


class ReadOnlyStorage(ReadableStorage):
    """
    Only implements ReadableStorage — honestly.
    Never inherits a write contract it cannot fulfil.
    Code that needs write access will get a type error at the call site,
    not a PermissionError at runtime.
    """

    def read(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()


def backup_file(storage: WritableStorage, src: str, dest: str) -> None:
    """Type system enforces that only WritableStorage can be passed here."""
    data = storage.read(src)
    storage.write(dest, data)


def display_file(storage: ReadableStorage, path: str) -> None:
    """Accepts both ReadOnlyStorage and LocalFileStorage — both are readable."""
    content = storage.read(path)
    print(content.decode())


# ── Demo ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    processor = PaymentProcessor()

    # Substitution works for every PaymentMethod — including FreeTrialPayment
    for method in [CreditCardPayment(), FreeTrialPayment()]:
        result = processor.process_payment(method, 100.0)
        print(result)

    # Shape hierarchy: no broken contract
    print_shape_info(Rectangle(400, 200))   # area: 80,000
    print_shape_info(Square(200))           # area: 40,000 — correctly, on its own terms

    # Storage: type system catches misuse before runtime
    local = LocalFileStorage()
    # backup_file(ReadOnlyStorage(), ...)  # TypeError at call site — caught early
