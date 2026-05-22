"""
LSP Violations: Subclasses that break their parent's contract.

Three patterns shown:
  1. Payment subclass that raises where base class never would
  2. Square inheriting Rectangle — the classic geometric trap
  3. ReadOnlyStorage inheriting FileStorage — throw on write/delete

In all three, the subclass IS-A parent by type, but breaks the
behavioural promise the parent made. Callers crash in places that
have nothing to do with the broken subclass.
"""

from abc import ABC, abstractmethod


# ══════════════════════════════════════════════════════════════════════════
# Violation 1 — Payment hierarchy
# PaymentProcessor calls get_fee() on every PaymentMethod.
# FreeTrialPayment raises instead of returning a number.
# The crash happens inside PaymentProcessor, not inside FreeTrialPayment.
# The bug is impossible to find by looking at the code that's failing.
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
        return round(amount * 0.02, 2)  # always returns a number

    @property
    def name(self) -> str:
        return "Credit Card"


class FreeTrialPayment(PaymentMethod):
    """
    Looks like a PaymentMethod. But it breaks the contract.
    get_fee() raises instead of returning a float.
    Any caller that does: fee = method.get_fee(amount) will crash here.
    """

    def process(self, amount: float) -> bool:
        print("Free trial — no charge applied")
        return True

    def get_fee(self, amount: float) -> float:
        # VIOLATION: base class contract says "return a float"
        # This raises instead. Every caller must now add a try/except
        # just to handle this one subclass — defeating the abstraction.
        raise NotImplementedError("Free trial has no fee — do not call get_fee()")

    @property
    def name(self) -> str:
        return "Free Trial"


class PaymentProcessor:
    def process_payment(self, method: PaymentMethod, amount: float) -> dict:
        fee = method.get_fee(amount)   # <-- CRASHES for FreeTrialPayment
        total = round(amount + fee, 2)
        success = method.process(total)
        return {"success": success, "amount": amount, "fee": fee, "total": total}


# ══════════════════════════════════════════════════════════════════════════
# Violation 2 — Rectangle / Square (the classic LSP trap)
# Geometrically, every Square IS-A Rectangle.
# But behaviourally, Square breaks Rectangle's contract:
# setting width and height independently produces wrong area.
# ══════════════════════════════════════════════════════════════════════════

class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def set_width(self, w: float) -> None:
        self.width = w

    def set_height(self, h: float) -> None:
        self.height = h

    def area(self) -> float:
        return self.width * self.height


class Square(Rectangle):
    """
    Maintains the square invariant: width == height always.
    But this breaks Rectangle's implicit contract:
      "setting width does not affect height, and vice versa."
    """

    def set_width(self, w: float) -> None:
        self.width = w
        self.height = w   # VIOLATION: side effect on height

    def set_height(self, h: float) -> None:
        self.width = h    # VIOLATION: side effect on width
        self.height = h


def resize_for_banner(shape: Rectangle) -> float:
    """Any caller expecting a Rectangle will be surprised by Square."""
    shape.set_width(400)
    shape.set_height(200)
    # Expected: 400 * 200 = 80,000
    # For Square: 200 * 200 = 40,000  <-- silent wrong result
    return shape.area()


# ══════════════════════════════════════════════════════════════════════════
# Violation 3 — ReadOnlyStorage inheriting FileStorage
# FileStorage promises: read, write, delete all work.
# ReadOnlyStorage throws on write and delete.
# Any code that accepts FileStorage and writes to it breaks silently.
# ══════════════════════════════════════════════════════════════════════════

class FileStorage:
    def read(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def write(self, path: str, data: bytes) -> None:
        with open(path, "wb") as f:
            f.write(data)

    def delete(self, path: str) -> None:
        import os
        os.remove(path)


class ReadOnlyStorage(FileStorage):
    def write(self, path: str, data: bytes) -> None:
        # VIOLATION: base class never raises here
        raise PermissionError("Storage is read-only")

    def delete(self, path: str) -> None:
        # VIOLATION: same problem
        raise PermissionError("Storage is read-only")


# ── Demo ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Violation 1
    processor = PaymentProcessor()
    try:
        processor.process_payment(FreeTrialPayment(), 100.0)
    except NotImplementedError as e:
        print(f"Payment crash: {e}")

    # Violation 2
    rect = Rectangle(100, 50)
    print(f"Rectangle area: {resize_for_banner(rect)}")   # 80,000 ✓
    sq = Square(100, 100)
    print(f"Square area: {resize_for_banner(sq)}")        # 40,000 ✗

    # Violation 3
    storage: FileStorage = ReadOnlyStorage()
    try:
        storage.write("/tmp/test.txt", b"hello")
    except PermissionError as e:
        print(f"Storage crash: {e}")
