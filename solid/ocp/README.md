# O — Open/Closed Principle

> "Software entities should be open for extension, but closed for modification." — Bertrand Meyer

## Files

| File | What it shows |
|------|---------------|
| `bad_example.py` | `PaymentProcessor` with an if/elif chain — every new payment type reopens this class |
| `good_example.py` | Abstract `PaymentMethod` (ABC + Protocol approaches) — new types are new classes, processor never changes |

## Run

```bash
python bad_example.py
python good_example.py
```

## Full Article

*LLD Chronicles #2 — coming soon on Medium*

---

← Back to [lld-python](../../README.md)
