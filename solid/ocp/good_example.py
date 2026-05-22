"""
OCP Applied: Open for extension, closed for modification.

PaymentProcessor never changes. To add Apple Pay, you write a new class.
Existing Credit Card and PayPal code is untouched — so it cannot break.

Two Python approaches shown:
  1. Abstract Base Class (ABC) — explicit contract, enforced at instantiation
  2. Protocol (typing.Protocol) — structural duck typing, no inheritance needed
"""

import logging
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════
# Approach 1 — Abstract Base Class
# Use when you want Python to enforce the interface at class instantiation.
# ══════════════════════════════════════════════════════════════════════════

class PaymentMethod(ABC):
    """Contract every payment method must fulfil. Never changes."""

    @abstractmethod
    def process(self, amount: float) -> bool:
        """Execute the payment. Returns True on success."""

    @abstractmethod
    def get_fee(self, amount: float) -> float:
        """Return the transaction fee for this method."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this payment method."""


class CreditCardPayment(PaymentMethod):
    def __init__(self, card_number: str, expiry: str):
        if len(card_number) != 16:
            raise ValueError("Card number must be 16 digits")
        self.card_number = card_number
        self.expiry = expiry

    def process(self, amount: float) -> bool:
        logger.info("Credit card charge: $%.2f (card ...%s)", amount, self.card_number[-4:])
        return True

    def get_fee(self, amount: float) -> float:
        return round(amount * 0.02, 2)  # 2%

    @property
    def name(self) -> str:
        return f"Credit Card (...{self.card_number[-4:]})"


class PayPalPayment(PaymentMethod):
    def __init__(self, email: str):
        if "@" not in email:
            raise ValueError("Invalid PayPal email")
        self.email = email

    def process(self, amount: float) -> bool:
        logger.info("PayPal charge to %s: $%.2f", self.email, amount)
        return True

    def get_fee(self, amount: float) -> float:
        return round(amount * 0.029, 2)  # 2.9%

    @property
    def name(self) -> str:
        return f"PayPal ({self.email})"


class CryptoPayment(PaymentMethod):
    def __init__(self, wallet_address: str, currency: str = "BTC"):
        self.wallet_address = wallet_address
        self.currency = currency

    def process(self, amount: float) -> bool:
        logger.info("%s payment to %s...: $%.2f", self.currency, self.wallet_address[:8], amount)
        return True

    def get_fee(self, amount: float) -> float:
        return 0.001  # flat fee regardless of amount

    @property
    def name(self) -> str:
        return f"{self.currency} ({self.wallet_address[:8]}...)"


# ── Adding Apple Pay? Write a NEW class. PaymentProcessor stays sealed. ───

class ApplePayPayment(PaymentMethod):
    def __init__(self, device_token: str):
        self.device_token = device_token

    def process(self, amount: float) -> bool:
        logger.info("Apple Pay charge: $%.2f", amount)
        return True

    def get_fee(self, amount: float) -> float:
        return 0.0  # no fee for Apple Pay

    @property
    def name(self) -> str:
        return "Apple Pay"


# ── PaymentProcessor: closed for modification, open for extension ──────────

class PaymentProcessor:
    """
    Knows nothing about Credit Card, PayPal, or Crypto specifically.
    Works with any PaymentMethod — including ones that don't exist yet.
    """

    def process_payment(self, method: PaymentMethod, amount: float) -> dict:
        fee = method.get_fee(amount)
        total = round(amount + fee, 2)
        success = method.process(total)
        logger.info("Payment via %s: $%.2f + $%.2f fee = $%.2f", method.name, amount, fee, total)
        return {"success": success, "method": method.name,
                "amount": amount, "fee": fee, "total": total}


# ══════════════════════════════════════════════════════════════════════════
# Approach 2 — Protocol (structural duck typing)
# Use when you don't want to force inheritance.
# Any class with .process() and .get_fee() qualifies — no ABC needed.
# ══════════════════════════════════════════════════════════════════════════

@runtime_checkable
class PaymentMethodProtocol(Protocol):
    def process(self, amount: float) -> bool: ...
    def get_fee(self, amount: float) -> float: ...
    @property
    def name(self) -> str: ...


class ProtocolAwareProcessor:
    """Accepts any object that structurally matches PaymentMethodProtocol."""

    def process_payment(self, method: PaymentMethodProtocol, amount: float) -> dict:
        if not isinstance(method, PaymentMethodProtocol):
            raise TypeError(f"{method} does not implement PaymentMethodProtocol")
        fee = method.get_fee(amount)
        total = round(amount + fee, 2)
        success = method.process(total)
        return {"success": success, "method": method.name,
                "amount": amount, "fee": fee, "total": total}


# ── Demo ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    processor = PaymentProcessor()

    methods = [
        CreditCardPayment("1234567812345678", "12/26"),
        PayPalPayment("alex@example.com"),
        CryptoPayment("1A2B3C4D5E6F7G8H", "ETH"),
        ApplePayPayment("device-token-xyz"),  # new method, zero changes to processor
    ]

    for method in methods:
        result = processor.process_payment(method, 100.0)
        print(result)
