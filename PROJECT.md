# Plate Editor project state

- Lifecycle: paused planned project
- Deployment type: none
- Repository role: independent pre-CNC editor plan
- GitHub implementation: README-only scaffold
- Canonical checkout: `~/src/editor-reidsurmeier-wtf`
- Default branch: `main`
- Public hostname: NXDOMAIN
- Reviewed: 2026-07-31

## Ownership boundary

This repository does not own a current service, Cloudflare route, GitHub Pages
site, or deployed artifact. It was intentionally created as a repository
separate from the Color Separator and CNC projects, but implementation stopped
after the initial README.

The four May 2026 planning documents recovered from the home research area are
preserved byte-for-byte under `docs/research/2026-05-08/`. Their proposed
ports, services, dependencies, and deployment steps are historical research,
not evidence of a live system.

## Verified state

Read-only checks on 2026-07-31 established:

- GitHub has one signed commit, one README, no workflow, and no Pages site.
- `editor.reidsurmeier.wtf` does not resolve in DNS.
- The Droplet has no matching systemd unit, nginx or cloudflared reference, or
  editor artifact in its managed application paths.
- No prior local Git checkout existed before the canonical additive clone was
  created at `~/src/editor-reidsurmeier-wtf`.

## Current objective

Preserve the original design work, make the repository documentation contract
explicit, and prevent planned infrastructure from being mistaken for current
state.

The first application tracer must be contract-first:

1. capture sanitized, representative output from the current Color Separator;
2. encode the accepted ZIP and manifest shape as a failing test;
3. encode the current CNC consumer requirements as a failing handoff test;
4. implement only the smallest lossless import/export path that makes both
   contracts pass;
5. reconsider framework versions and deployment only after that vertical slice
   is green.

## Validation

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 -m compileall -q tests
```
