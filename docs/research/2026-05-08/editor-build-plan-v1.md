# editor.reidsurmeier.wtf — Master Build Plan v1

**Date:** 2026-05-08
**Status:** Synthesis from 12-agent ruflo swarm + 2 deep-assessments + 13 prior research streams. NO code written yet.
**Repo:** https://github.com/ReidSurmeier/editor-reidsurmeier-wtf (created, just blank README)

---

## 1. Position + intent

A pre-CNC plate editor sitting between `color.reidsurmeier.wtf` (color-separator) and `cnc.reidsurmeier.wtf` (CNC milling).

**Job:** read color-sep's ZIP, consolidate plates (3 reds → 1), strip ghost detail too small to mill, emit a ZIP that cnc ingests unchanged.

**MVP cut (10 days):** ZIP-in → plate list → cluster suggestions → one-click accept → ghost-filter → ZIP-out → Cmd+Z undo. Hand-mode defaults only.

**Phase 2:** OKLCH popover · live composite via spectral.js GLSL · underprint expansion · block packing · CNC mode toggle · drag-drop merge · history snapshots · custom palette · wasted-area stat.

---

## 2. Locked decisions (resolved conflicts)

| Decision | Lock |
|---|---|
| Domain | `editor.reidsurmeier.wtf` (public, no auth) |
| Repo | `ReidSurmeier/editor-reidsurmeier-wtf` (separate, public) |
| Local repo path | `~/src/editor-reidsurmeier-wtf` |
| Frontend port | 3013 |
| Backend port | **8011** (resolves 4-way conflict — backend + devops aligned, neighbor of knowledge-engine :8010) |
| Scratch dir | `/var/lib/editor/jobs/<job_id>/` 6h TTL, dual-cleanup (anyio + systemd timer) |
| API shape | **Nested** `/api/v1/projects/{id}/...` (not flat) |
| Manifest namespace | `editor.*` only — `press.*` purged |
| Merge cardinality | **N≥2** (must support "3 reds → 1") |
| ΔE metric | **Cluster geometry: ΔE_oklab. Threshold gate: ΔE2000 (CIELab).** Convert OKLab→XYZ→Lab via colour-science. |
| Jaccard gate | **0.0 in MVP** (no spatial gate). Add ≥0.4 gate Phase 2. |
| K-M server-side | **Dropped from MVP.** sRGB-α composite for preview is fine — cnc doesn't read composite. spectral.js Phase 2 only. |
| Filename rank | Import filenames stable. New print order in `manifest.editor.print_order[]`. |
| TS types | **Generated** via `datamodel-code-generator` from FastAPI OpenAPI. Hand-written types banned. |
| Pigment language | "Pigment", NOT "ink" (water-based mokuhanga) |
| Mode in MVP | **Hand only.** CNC mode Phase 2. |

---

## 3. Architecture topology

```
┌─────────────────────────────────────────────────────────────┐
│ user browser                                                │
│   ↓ HTTPS                                                   │
│ Cloudflare tunnel → editor.reidsurmeier.wtf (proxied)      │
│   ↓                                                         │
│ ┌─────────────────────────────────────────┐                 │
│ │ editor-frontend.service (port 3013)     │                 │
│ │ Next.js 16 standalone SSR               │                 │
│ │ rewrites /api/v1/* → backend            │                 │
│ └────────────────┬────────────────────────┘                 │
│                  ↓ same-origin (no CORS)                    │
│ ┌─────────────────────────────────────────┐                 │
│ │ editor-backend.service (127.0.0.1:8011) │                 │
│ │ uvicorn --workers 2                     │                 │
│ │ FastAPI                                 │                 │
│ │ scratch: /var/lib/editor/jobs/<uuid>/   │                 │
│ └─────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### Frontend stack (pinned)
- Next.js 16.2.1 (App Router, standalone, Turbopack with `--webpack` fallback if Turbo bug bites)
- React 19.2.4
- Tailwind v4 (expect 1-2 days fighting `cn`/`cva` rewrites — shadcn templates still v3)
- shadcn/ui + Lucide icons
- @texel/color (3.5 KB OKLCH)
- clipper2-js (preview-only — server is authoritative)
- dnd-kit (Phase 2; react-dnd dead on React 19)
- Zustand v5 + IndexedDB blob store (NOT localStorage — quota too tight for ZIP blobs)
- openapi-typescript codegen for type sync

### Backend stack (pinned)
- Python 3.12, uv-managed venv
- fastapi 0.136.1 + uvicorn 0.46.0 + pydantic 2.13.4
- numpy 2.4.4 + scipy 1.17.1 + Pillow 12.2.0
- **pyclipr 0.1.8** (NOT pyclipper — Clipper1 chokes on potrace self-intersections)
- simplification 0.7.14 (Visvalingam-Whyatt)
- colour-science 0.4.7 + scikit-image (morphology, dilation)
- structlog 25.5.0 + JSON to stdout → systemd journal
- pytest 9.0.3 + pytest-asyncio 1.3.0

---

## 4. Domain model

**One aggregate root: `Project`.** One bounded context: Editing.

```
Project (aggregate root)
├── plates: Plate[]
│   ├── id, index (k-means centroid, color-sep index)
│   ├── rank (1..N, print order)
│   ├── name (plate1..plateN)
│   ├── color: { rgb, hex, oklab }
│   ├── coverage_pct
│   ├── filename (ZIP-only, "<rank>_<hex>")
│   ├── patches: Patch[]  (≥1 per plate)
│   ├── pigment: PigmentRef
│   └── editor: { dropped_paths, simplified_paths, source_index_origin }
├── pigments: PigmentLibrary  (mokuhanga preset hardcoded MVP)
├── mode: "hand"  (only Hand in MVP)
├── printOrder: number[]  (light→dark, derived from rank, mutable Phase 2)
├── history: Snapshot[]  (auto before each merge, max 50)
├── source: { manifest_hash, version: "v20", upscaled, paper_pct, sam_masks }
└── editorVersion: 1
```

**ACL boundary:** `backend/app/services/zip_io.py` (Python) + `frontend/src/lib/manifest_acl.ts` (TS). Color-sep's manifest is external published language; domain code never sees raw shape.

**10 invariants** (most critical):
1. ZIP roundtrip is byte-equivalent for unedited fields
2. `png/<filename>.png` ↔ `svg/<filename>.svg` 1:1 always
3. `plates[].index` (k-means centroid) preserved through merges
4. `plates[].filename` synthesized only at ZIP-write time (not in API responses)
5. Kento marks pass through unchanged (color-sep doesn't have any → cnc generates them; editor never touches that zone)
6. Mask resolution preserved at full source resolution (no downscale policy)
7. `merge_suggestions` from color-sep stripped on export, recomputed by editor
8. `editor.original_manifest_hash` set on import for drift detection
9. Print order is `light→dark` (rank=1 = lightest) — invariant for MVP
10. Plate centroid in OKLab, weight-averaged by coverage, roundtripped to sRGB on emit

**Anti-corruption notes** (from color-sep assessment):
- 3 dead filter params (`shadow_threshold`, `highlight_threshold`, `median_size`) — DO NOT surface to editor UI
- K-means centroid `index`, not `rank`, is the stable identifier across merges
- K-means non-deterministic across BLAS thread counts even with `random_state=42` — never assume plate IDs match between separate runs
- `merge_pairs` for color-sep's `/api/merge` uses `index` not `rank` (editor doesn't call this in MVP, but if Phase 2 hooks back, get this right)

---

## 5. API surface (MVP)

```
POST /api/v1/projects/import           multipart ZIP → Project + manifest expanded
GET  /api/v1/projects/{id}             Project state
POST /api/v1/projects/{id}/suggest-merges  body: {threshold_dE2000, mode} → suggestions[]
POST /api/v1/projects/{id}/apply-merge body: {plateIds: string[], idemKey} → updated Project
POST /api/v1/projects/{id}/cleanup     body: {tool_diameter_mm, simplify_tol_px, min_area_factor} → updated Project + stats
POST /api/v1/projects/{id}/composite   body: {format: "png", quality: "preview"} → PNG bytes (sRGB-α)
POST /api/v1/projects/{id}/export      → ZIP bytes (cnc-compatible)
GET  /api/v1/health                    {ok, version}
GET  /api/v1/openapi.json              auto-generated
```

**Deferred to Phase 2:** SSE for cluster progress, idempotency keys, `if-match` etag two-tab guard, `/composite` quality=export, R2 presigned URLs.

**Caps:**
- Upload: **100 MB** (CF Free-plan limit per reviewer)
- Extracted: 1 GB total / 200 MB per file (ZIP-bomb defense)
- PNG: 67 Mpx max
- Rate: 60 req/min, 10 uploads/min per IP

---

## 6. Algorithm specs

### Plate-merge clustering
```python
def cluster_plates(plates, mode, threshold_dE2000=6.0):
    # 1. distance matrix in OKLab, coverage-weighted
    D = oklab_distance_matrix_weighted(plates)  # d = ΔE_oklab / max(0.2, min(cov)^0.5)
    # 2. complete-linkage agglomerative
    Z = scipy.cluster.hierarchy.linkage(D, method="complete")
    # 3. cut where new merge would push max-pairwise ΔE2000 (CIELab) > threshold
    clusters = cut_dendrogram_by_max_dE2000(Z, plates, threshold_dE2000)
    # 4. emit suggestions sorted by ΔE ascending, top 5
    return [{
        cluster_id, plate_ids: [...],
        suggested_centroid_rgb,  # coverage-weighted mean in OKLab → sRGB
        max_internal_dE2000,
        total_coverage_pct
    } for c in clusters]
```

### Ghost-detail filter
```python
def clean_plate(plate, tool_diameter_mm=3.175, simplify_tol_px=0.5, min_area_factor=3):
    # SIMPLIFY first (Visvalingam-Whyatt), tol clamped ≤ r/2
    paths = vw_simplify(plate.svg_paths, tolerance=min(simplify_tol_px, r_eff_px/2))
    # FILTER second: pyclipr ClipperOffset(-r_eff)
    r_eff = tool_diameter_mm / 2
    eroded = pyclipr.offset(paths, -r_eff)
    A_min = π * (r_eff * min_area_factor)**2  # ≈ 17.8 mm² for 1/8" bit
    kept = [p for p in eroded if p.area > A_min]
    return cleaned_plate(paths=kept, stats={dropped, simplified})
```

**Performance budget:** sub-5s total for typical project (≤30 plates, ≤4096²).

---

## 7. UX layout (MVP)

```
┌─────────────────────────────────────────────────────────────┐
│ editor.reidsurmeier.wtf       Hand mode    [Export ZIP]      │
├─────────────────┬───────────────────────────────────┬───────┤
│ PLATES (6)      │                                   │ DETAILS│
│                 │                                   │        │
│ [👁] ▌ red    14│       composite preview           │ Plate  │
│ [👁] ▌ red    8 │       (sRGB-α PNG from server,    │ red_dc │
│ [👁] ▌ red    3 │        zoom/pan via CSS,          │ #DC2828│
│ [👁] ▌ blue   22│        ghost overlay = red fill,  │ 14.2%  │
│ [👁] ▌ blk    31│        cmd-click = solo)          │        │
│ [👁] ▌ paper  18│                                   │        │
│                 │                                   │        │
│ ── SUGGESTIONS  │                                   │        │
│ Plates 1+2+3 ΔE │                                   │        │
│ 3.8  [✓ accept] │                                   │        │
│                 │                                   │        │
│                 │                                   │        │
└─────────────────┴───────────────────────────────────┴───────┘

[Drop ZIP zone if no project loaded]
```

**Interactions (MVP only):**
- Click eye → toggle visibility (composite re-renders, debounced + AbortController)
- Cmd+click row → solo
- Click suggestion ✓ → auto-snapshot + apply merge
- Cmd+Z → undo (linear, max 50 snapshots, IndexedDB persist)
- Drop ZIP → import
- Click Export → download ZIP

**Deferred to Phase 2:** drag-drop merge, multi-select+M, named snapshots UI, OKLCH popover, custom palette editor, wasted-area stat, recent projects, mode toggle UI.

**Visuals:** Inter UI + font-mono filenames. Default Tailwind + Claude orange accent. Ghost overlay red fill + diagonal stripe (color-blindness affordance — caught by reviewer).

---

## 8. Build sequence (10 days)

| Day | Owner | Output | Blocks |
|---|---|---|---|
| **D0** | dispatcher | port lock, scratch path lock, repo skeleton, CONTRACTS.md, `cnc-ingest-spec.md` | everything |
| **D1** | backend | shared-types codegen pipeline (datamodel-code-generator → TS) | D2+ |
| **D2** | backend | ZIP roundtrip + ACL (`zip_io.py` + `manifest_acl.ts`), byte-identical test | D3+, D5+ |
| **D3** | algorithm | `cluster_plates` + `oklab_distance_matrix_weighted`, unit tests w/ canonical 3-reds fixture | D6 |
| **D4** | algorithm | `clean_plate` (VW + pyclipr erosion), unit tests w/ thin-line fixture | D6 |
| **D5** | frontend | Next.js skeleton, ZIP drop zone, PlateStack + composite from server, Zustand store + IndexedDB | D6 |
| **D6** | dispatcher | FE↔BE wiring: import, suggest, apply-merge, cleanup, composite. End-to-end happy path. | D7 |
| **D7** | frontend | snapshot history (auto before merge), Cmd+Z, ghost overlay toggle, color-blind stripe, error toasts | D8 |
| **D8** | tester | export QA: ZIP byte-roundtrip + cnc.reidsurmeier.wtf actually ingests output. Real-image fixtures. | D9 |
| **D9** | devops + dispatcher | systemd units, CF tunnel ingress, deploy script, build script (find server.js dynamically), CF cache purge | D10 |
| **D10** | tester + user | real-image QA loop on 3 canonical ZIPs from past color-sep work | ship |

**Critical path:** port lock → shared types → byte-identical roundtrip → deterministic cluster fixture → cnc ingest contract → deploy.

---

## 9. Test plan (real-image only, anti-synth lint rule)

### Canonical fixtures (Git LFS, sha256-pinned)
- `tests/fixtures/zip/kawase_hiroshige_3plate.zip` (3 plates, edge case: minimum)
- `tests/fixtures/zip/mt_fuji_8plate_3reds.zip` (8 plates with the load-bearing 3-reds case)
- `tests/fixtures/zip/urban_sketch_15plate_thinlines.zip` (15+ plates with sub-mill features)

### Required tests (priority order)
1. ZIP byte-roundtrip — import → no-op edits → export → bit-identical for unedited fields
2. **CNC ingest contract test** — `cnc.import(editor.export(colorsep.emit()))` succeeds — staging cnc endpoint stub
3. cluster: 3-reds case must merge to size 3 with centroid ΔE2000 ≤ 4 from each member
4. cluster: 2 perceptually-distant reds must NOT merge
5. cleanup: thin-line fixture must drop sub-A_min paths, retain main shape
6. Playwright smoke: drop ZIP → see plates → accept suggestion → export → assert merged manifest
7. Bad-ZIP error toast (corrupted manifest, missing png/, missing svg/)
8. Refresh recovers state from IndexedDB
9. ZIP-bomb refuse (4 GB / 100x ratio)
10. Visual regression on composite preview (≤0.5% pixel diff at 1280×800)

**Coverage targets:** 80% backend, 60% frontend, 100% MVP API routes have ≥1 E2E.

**Performance gates:** cluster 30-plate <10s, export 30-plate <30s, composite re-render <500ms.

---

## 10. Deploy

```bash
# repo path
~/src/editor-reidsurmeier-wtf/
├── frontend/   # Next.js (flat sibling — avoids monorepo standalone-path trap)
├── backend/    # FastAPI + uv venv
└── scripts/build.sh deploy.sh

# build.sh (key snippet)
SERVER_JS=$(find frontend/.next/standalone -name server.js -maxdepth 3)
cp -r frontend/.next/static frontend/.next/standalone/.next/
cp -r frontend/public frontend/.next/standalone/

# systemd units
~/.config/systemd/user/
├── editor-frontend.service  (ExecStart: node frontend/.next/standalone/.../server.js, port 3013)
├── editor-backend.service   (ExecStart: backend/.venv/bin/uvicorn ..., 127.0.0.1:8011, --workers 2)
└── editor-gc.timer + .service  (sweep /var/lib/editor/jobs/ older than 6h, every 30 min)

# CF tunnel ingress (add to existing tunnel)
- hostname: editor.reidsurmeier.wtf
  service: http://localhost:3013

# CF mode: Proxied (orange cloud) — short-lived requests, no 524 risk
# After deploy: curl /api/cloudflare/.../purge_cache
```

**Health check:** `curl -sf http://localhost:8011/api/v1/health` returns `{"ok": true, "version": "..."}`.

**Logs:** `journalctl --user -u editor-frontend.service` and `editor-backend.service`.

**Rollback:** `git tag pre-deploy-{ts}` before each deploy; rollback script reverts + rebuilds.

---

## 11. Risks + mitigations

| Risk | Mitigation |
|---|---|
| pyclipr 0.1.8 wheel availability on Py 3.12 | Verify wheel during D0 setup; fallback: build from source via maturin (clipper2 has CI builds) |
| shadcn-on-Next-16 instability (Turbopack standalone bug per CLAUDE.md) | Build with `--webpack` flag from D5 |
| Tailwind v4 + shadcn template incompat | Budget 1-2 days at D5 fighting `cn`/`cva` rewrites |
| CF Free-plan 100MB upload limit | Cap at 100MB (matches reviewer) |
| Color-sep schema drift (silent) | Pin `version` whitelist `{v18, v19, v20, v21}`; warn banner on unknown |
| K-means non-determinism across machines | `editor.original_manifest_hash` for drift detection; never assume plate IDs across runs |
| ZIP-bomb on public endpoint | 1GB / 100x ratio refuse, 200MB per-file |
| BE workers=2 × 4096² masks RAM blowout | Resolution upper bound check at import; reject >67Mpx |
| 5 npm deps unused in cnc tool (svgo, etc.) | Editor takes the cleanup work; cnc remains untouched |
| Two-tab clobber via Zustand persist | `storage` event listener + warn toast (Phase 2 — MVP single-tab assumption) |

---

## 12. Pre-code action list (do these BEFORE D0)

1. **Bootstrap repo** at `~/src/editor-reidsurmeier-wtf/` (clone GitHub stub, create `frontend/` + `backend/` + `scripts/` + `tests/fixtures/zip/`)
2. **CONTRACTS.md** with locked decisions table from §2
3. **cnc-ingest-spec.md** documenting the contract test (input shape cnc requires, output shape editor produces)
4. **PIPELINE-STATE.md** specialist assignments per §8
5. **datamodel-code-generator config** — generates `frontend/src/types/api.ts` from `backend/app/main.py` OpenAPI dump
6. **Verify pyclipr wheel** — `uv pip install pyclipr==0.1.8` in a throwaway venv, smoke-test import
7. **Pull 3 canonical ZIPs from your past color-sep outputs** to `tests/fixtures/zip/`, sha256-pin
8. **Lock-domain-language ESLint rule** — bans `layer`, `screen`, `ink`, `underbase`
9. **Lock-domain-language ruff rule** — same banned terms in Python
10. **CF tunnel ingress entry** for `editor.reidsurmeier.wtf` (don't deploy yet, just add the route)

---

## 13. Cut list (out of scope, all phases)

- bokashi simulator (guidance text only)
- multi-user accounts
- telemetry / analytics
- iframe-embedded CNC tool
- direct-handoff R2 (Phase 2 if needed)
- polygon nesting (SVGnest) — Phase 3 if wood waste becomes painful
- dark→light opaque print order
- node-graph editor
- AI auto-recolor
- per-pass V-bit calculator (CNC tool's job)
- 3 dead color-sep filter params (shadow/highlight/median) — never surface

---

## 14. Open questions still pending

These didn't get answered in the grill but won't block D0:

- Q11 Bokashi (locked: skip + guidance text)
- Q14 Underprint ε default (Phase 2)
- Q15 Trap/choke value (Phase 2 — MVP is Hand-only with 0.25mm trap if reachable, else skip)
- Q17 Mokuhanga palette (Phase 2 — MVP just shows hex swatch)
- Q18 "Clearly apart" threshold (Phase 2)
- Q19/Q20 Print order editable (Phase 2)
- Q22 History model — locked: linear with auto-snapshot before merge, no named snapshot UI in MVP
- Q25 Save format — locked: IndexedDB blob store + project state JSON; reload prompts re-upload if blob missing
- Q26 Layout — locked: single page

---

## 15. Sign-off needed before D0

- Port lock 3013/8011 ✓
- Scratch path `/var/lib/editor/jobs/<job_id>/` 6h ✓
- Nested API shape ✓
- ΔE metric: ΔE_oklab cluster / ΔE2000 gate ✓
- editor.* manifest namespace ✓
- pyclipr 0.1.8 ✓
- shadcn + Tailwind v4 + Next 16 (expect 1-2 day tooling cost) ✓
- 100 MB upload cap (CF Free-plan reality) ✓
- Hand-mode-only MVP (CNC mode Phase 2) ✓
- IndexedDB blob + project state JSON, no localStorage for ZIPs ✓
- 3 canonical real-image ZIPs from past color-sep work ✓
- 10-day MVP build sequence ✓

**If all 12 lock items above are accepted, D0 can begin.**
