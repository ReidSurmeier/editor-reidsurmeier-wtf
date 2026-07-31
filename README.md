# editor.reidsurmeier.wtf

A planned pre-CNC editor for consolidating color-separation output into
milling-ready plates and blocks for water-based pigment woodblock printing.

## Current status

This repository is a paused, README-only project scaffold. It has no
application implementation, deployment, GitHub Pages site, or live hostname.
The May 2026 design work is preserved under
[`docs/research/2026-05-08/`](docs/research/2026-05-08/README.md), but those
documents describe historical plans rather than current runtime state.

Read [`PROJECT.md`](PROJECT.md) for verified project state,
[`CONTEXT.md`](CONTEXT.md) for domain language, and
[`docs/adr/0001-preserve-the-paused-plan.md`](docs/adr/0001-preserve-the-paused-plan.md)
for the governing decision.

## Validation

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```
