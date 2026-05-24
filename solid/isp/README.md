# ISP — Interface Segregation Principle

> "Clients should not be forced to depend on methods they do not use."

Part of the [LLD Chronicles](https://medium.com/@pavankumarmasters) series on SOLID principles in Python.

## What This Covers

The Interface Segregation Principle states that no client should be forced to depend on methods it does not use. Fat interfaces force implementing classes to stub methods they can't support — creating silent `NotImplementedError` traps and coupling classes to changes in code they never call.

Three violation patterns are shown:

| Violation | What breaks |
|-----------|------------|
| `OfficeDevice` forces `BasicPrinter` to implement scan, fax, and staple | BasicPrinter stubs 3 methods it can never honour |
| `PipelineWorker` forces `AnalyticsWorker` to implement export, email, archive | Analytics service recompiles when email signature changes |
| `UserService` forces `AuditService` to implement write, email, and export | Read-only compliance service breaks on every new feature |

## Files

- [bad_example.py](bad_example.py) — Three ISP violations (fat interfaces with stubs)
- [good_example.py](good_example.py) — Three ISP fixes (segregated interfaces + Protocol approach)

## Key Concepts Demonstrated

- **Narrow ABC interfaces** — split at capability boundaries
- **Multiple interface composition** — `AllInOnePrinter(Printable, Scannable, Faxable, Stapleable)`
- **Caller functions with minimal dependencies** — `print_batch(printer: Printable)` cannot call `scan_document()`
- **Python Protocols** — structural subtyping, no inheritance needed

## The ISP Rule

Split when different clients have materially different views of the interface. If they all need the same methods, the interface is the right size.

## Article

[The I in SOLID: Interface Segregation Principle in Python | LLD Chronicles #4](https://medium.com/@pavankumarmasters)

## Related

- [SRP article](../srp/README.md)
- [OCP article](../ocp/README.md)
- [LSP article](../lsp/README.md)
