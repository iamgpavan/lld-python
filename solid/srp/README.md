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

*LLD Chronicles #1 — coming soon on Medium*

---

← Back to [lld-python](../../README.md)
