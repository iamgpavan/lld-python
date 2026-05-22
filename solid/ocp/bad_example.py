"""
OCP Violation: The if/elif Chain
Every new payment method requires reopening and modifying PaymentProcessor.
Adding "Apple Pay" means touching code that already handles Credit Card and PayPal.
If Credit Card breaks after the Apple Pay change, that's on you.
"""

import logging

logger = logging.getLogger(__name__)


class PaymentProcessor:
    """
    Processes payments. Knows about every payment method by name.
    Adding a new method = modify this class = risk breaking existing methods.
    """

    def process(self, payment_type: str, amount: float, **kwargs) -> dict:
        if payment_type == "credit_card":
            card_number = kwargs.get("card_number", "")
            expiry = kwargs.get("expiry", "")
            # Credit card specific validation
            if not card_number or len(card_number) != 16:
                return {"success": False, "error": "Invalid card number"}
            fee = round(amount * 0.02, 2)  # 2% fee
            total = amount + fee
            logger.info("Credit card charge: $%.2f (fee: $%.2f)", amount, fee)
            return {"success": True, "method": "credit_card", "amount": amount,
                    "fee": fee, "total": total}

        elif payment_type == "paypal":
            email = kwargs.get("email", "")
            if not email or "@" not in email:
                return {"success": False, "error": "Invalid PayPal email"}
            fee = round(amount * 0.029, 2)  # 2.9% fee
            total = amount + fee
            logger.info("PayPal charge to %s: $%.2f (fee: $%.2f)", email, amount, fee)
            return {"success": True, "method": "paypal", "amount": amount,
                    "fee": fee, "total": total}

        elif payment_type == "crypto":
            wallet = kwargs.get("wallet_address", "")
            currency = kwargs.get("currency", "BTC")
            if not wallet:
                return {"success": False, "error": "Invalid wallet address"}
            fee = 0.001  # flat fee
            total = amount + fee
            logger.info("%s payment to %s...: $%.2f", currency, wallet[:8], amount)
            return {"success": True, "method": "crypto", "amount": amount,
                    "fee": fee, "total": total}

        # ── Adding Apple Pay? Open this class. Add an elif. ─────────────────
        # ── Adding Google Pay? Open this class. Add an elif. ────────────────
        # ── Adding bank transfer? Open this class. Add an elif. ─────────────
        # Every new method risks breaking Credit Card, PayPal, and Crypto.

        else:
            raise ValueError(f"Unknown payment type: '{payment_type}'")

    def get_fee(self, payment_type: str, amount: float) -> float:
        """Fee calculation is also buried in this class. Same problem."""
        if payment_type == "credit_card":
            return round(amount * 0.02, 2)
        elif payment_type == "paypal":
            return round(amount * 0.029, 2)
        elif payment_type == "crypto":
            return 0.001
        else:
            raise ValueError(f"Unknown payment type: '{payment_type}'")


# ── Demo ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    processor = PaymentProcessor()

    # Works fine — until a new payment type arrives and someone
    # introduces a bug in the elif chain while adding it.
    print(processor.process("credit_card", 100.0, card_number="1234567812345678"))
    print(processor.process("paypal", 50.0, email="user@example.com"))
    print(processor.process("crypto", 200.0, wallet_address="1A2B3C4D5E6F7G8H"))
