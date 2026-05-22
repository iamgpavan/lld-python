# LSP — Liskov Substitution Principle

> "If it walks like a duck, it must also quack like a duck."

Part of the [LLD Chronicles](https://medium.com/@pavankumarmasters) series on SOLID principles in Python.

## What This Covers

The Liskov Substitution Principle states that objects of a subclass must be substitutable for objects of the parent class without altering the correctness of the program.

Three violation patterns are shown:

| Violation | What breaks |
|-----------|------------|
| `FreeTrialPayment.get_fee()` raises `NotImplementedError` | Postcondition — parent promises a float return |
| `Square(Rectangle)` — `set_width()` silently changes height | Invariant — parent promises width and height are independent |
| `ReadOnlyStorage(FileStorage)` — `write()` raises `PermissionError` | Precondition strengthened — caller trusted the parent's contract |

## Files

- [bad_example.py](bad_example.py) — Three LSP violations
- [good_example.py](good_example.py) — Three LSP fixes

## The Three LSP Rules

1. **Preconditions cannot be strengthened** — subclass cannot reject inputs the parent accepts
2. **Postconditions cannot be weakened** — subclass cannot return less or raise where parent returned a value
3. **Invariants must be preserved** — subclass cannot silently couple state the parent kept independent

## The Substitution Test

Take every test written for the parent class. Run it against the subclass. Every single test must pass.

A test failure = an LSP violation found before it crashes production.

## Article

[The L in SOLID: Liskov Substitution Principle in Python | LLD Chronicles #3](https://medium.com/@pavankumarmasters)

## Related

- [SRP article](../srp/README.md)
- [OCP article](../ocp/README.md)
