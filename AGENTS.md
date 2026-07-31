# Plate Editor agent guide

This repository preserves the plan for `editor.reidsurmeier.wtf`; it does not
yet contain an application. Read `PROJECT.md`, then `CONTEXT.md`, and consult
accepted decisions under `docs/adr/` before changing scope, terminology, or
deployment claims.

Treat documents under `docs/research/2026-05-08/` as immutable historical
inputs. They are evidence, not current operational instructions. Do not deploy,
register DNS, create services, or install the proposed dependency stack as a
side effect of tests.

Use test-driven development for implementation. The first implementation
slice must establish a current, fixture-backed ZIP contract with the upstream
Color Separator and downstream CNC consumer before selecting or installing
the historical framework versions.

## Commands

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 -m compileall -q tests
```

## Agent skills

### Issue tracker

Issues and PRDs live in GitHub Issues for
`ReidSurmeier/editor-reidsurmeier-wtf`. See
`docs/agents/issue-tracker.md`.

### Triage labels

Use the five standard Matt Pocock triage roles. See
`docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repository with `CONTEXT.md` at the root and
decisions in `docs/adr/`. See `docs/agents/domain.md`.
