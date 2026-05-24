# DIP — Dependency Inversion Principle

> "High-level modules should not depend on low-level modules. Both should depend on abstractions."

Part of the [LLD Chronicles](https://medium.com/@pavankumarmasters) series on SOLID principles in Python.

## What This Covers

The Dependency Inversion Principle states that business logic should never reach down and grip a concrete infrastructure detail. The dependency arrows should point toward abstractions — not toward databases, filesystems, or external services. Details are injected from outside; business logic never creates them.

Three violation patterns are shown:

| Violation | What breaks |
|-----------|------------|
| `OrderService` instantiates `MySQLOrderRepository` directly | Switching to Postgres requires editing business logic |
| `NotificationService` creates `SmtpEmailSender` and `TwilioSmsSender` | Adding Slack requires editing the notification orchestrator |
| `ReportGenerator` calls `open()` and `csv.writer` directly | Uploading to S3 requires rewriting report generation logic |

## Files

- [bad_example.py](bad_example.py) — Three DIP violations (tight coupling to infrastructure)
- [good_example.py](good_example.py) — Three DIP fixes (injected abstractions + composition root)

## Key Concepts Demonstrated

- **ABC abstractions as dependency boundaries** — `OrderRepository`, `NotificationSender`, `DataWriter`
- **Constructor injection** — the primary DI pattern used throughout
- **Test doubles** — `InMemoryOrderRepository`, `SilentSender`, `InMemoryWriter`
- **Composition root** — `create_production_stack()` vs `create_test_stack()`
- **Python Protocol** for structural DIP without explicit inheritance
- **DIP vs DI** — the principle vs the technique

## The Dependency Inversion

```
Before:  OrderService ──→ MySQLOrderRepository
After:   OrderService ──→ OrderRepository ←── MySQLOrderRepository
                                          ←── InMemoryOrderRepository (tests)
                                          ←── PostgresOrderRepository (future)
```

Both the high-level module and the low-level details now point toward the abstraction.

## Article

[The D in SOLID: Dependency Inversion Principle in Python | LLD Chronicles #5](https://medium.com/@pavankumarmasters)

## Related

- [SRP article](../srp/README.md)
- [OCP article](../ocp/README.md)
- [LSP article](../lsp/README.md)
- [ISP article](../isp/README.md)
