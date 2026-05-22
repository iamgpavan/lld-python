# S — Single Responsibility Principle

> "A class should have only one reason to change." — Robert C. Martin

## Files

| File | What it shows |
|------|---------------|
| `bad_example.py` | `UserManager` — one class handling DB, email, reports, logging, and validation |
| `good_example.py` | Five focused classes + a thin `UserService` orchestrator |

## Run

```bash
python bad_example.py
python good_example.py
```

## Full Article

[The S in SOLID: Single Responsibility Principle in Python](https://medium.com/@pavankumarmasters/the-s-in-solid-single-responsibility-principle-in-python-lld-chronicles-1-03ae1bcc9678)

---

← Back to [lld-python](../../README.md)
