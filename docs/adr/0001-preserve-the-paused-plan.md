# ADR 0001: Preserve the paused plan without claiming a runtime

- Status: accepted
- Date: 2026-07-31

## Context

`ReidSurmeier/editor-reidsurmeier-wtf` was created on 2026-05-08 after a
detailed design and grilling session. The GitHub repository stopped at a
README-only initial commit, while four substantially larger planning documents
remained in the home research area.

Several statements in those documents are proposals: framework versions,
ports, systemd units, Cloudflare ingress, storage paths, and deployment
commands. Current checks find no implementation, no GitHub Pages site, no DNS
record, and no deployment on the Droplet. Treating those proposals as live
operations would create false ownership and could collide with current
services.

The editor also sits on a contract boundary between two independently changing
projects. Implementing the historical plan before verifying both current
contracts would risk preserving an obsolete ZIP shape.

## Decision

Treat this repository as a paused planned project with no deployment.

- Preserve the four source documents byte-for-byte as historical research
  inputs, with checksums and provenance.
- Keep current lifecycle and runtime claims in `PROJECT.md`.
- Keep current domain language in `CONTEXT.md`.
- Do not activate the proposed services, DNS, dependencies, or ports merely
  because they appear in the historical plan.
- Begin any future implementation with a fixture-backed import/export tracer
  against the current Color Separator and CNC contracts.
- Use Git history and ADRs for reviewed changes rather than rewriting the
  recovered source documents.

## Consequences

The design work remains available without manufacturing a deployment history.
The project is documentation-conformant and ready for a narrow TDD tracer, but
none of the historical technology selections are automatically current.
