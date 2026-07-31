# editor.reidsurmeier.wtf — Context

A pre-CNC tool that consolidates color-separation output into milling-ready plates and blocks for water-based pigment woodblock printing. Sits between `color.reidsurmeier.wtf` (color-separator) and `cnc.reidsurmeier.wtf` (CNC milling).

## Language

**Plate**:
One pigment + its mask. One color, may have multiple non-touching patches. The thing `color.reidsurmeier.wtf` emits in `manifest.plates[]`.
_Avoid_: screen, layer, color (too generic)

**Block**:
One physical piece of carved wood. Carries 1+ plates. Has stock size, grain orientation, kento marks.
_Avoid_: board, panel

**Patch**:
One connected region within a plate. A plate has ≥1 patches.

**Pigment**:
The water-based color material assigned to a plate (e.g. sumi, gofun, gamboge, vermillion, indigo, bengala). May be a single pigment or a mixed recipe with nori paste. Mokuhanga water-based, NOT oil ink.
_Avoid_: ink (incorrect for mokuhanga workflow)

**Trap**:
A small overlap between two adjacent plates to hide misregistration. Adopted from screenprint vocabulary.

**Choke**:
Inset a plate edge inward by a chosen distance. Used in underprint expansion to pull back from the edge of a covering plate above.

**Spread**:
Grow a plate edge outward by a chosen distance. Inverse of choke.

**Underprint**:
A plate's expanded mask extending into pixels that will be fully covered by later plates above it in print order. Specific to translucent water-based pigment workflow on white washi: visible composite invariant within ε ΔE2000.
_Avoid_: underbase (screenprint term, wrong physics for translucent-under-translucent)

**Hand mode**:
Project setting where blocks will be carved and printed by hand baren on washi. Registration tolerance 0.3–0.5 mm. Aggressive plate merging, larger trap default (~0.25 mm).

**CNC mode**:
Project setting where blocks are CNC-milled and printed with mechanical press or careful hand alignment. Registration tolerance <0.1 mm. Permissive plate merging, tiny or zero trap default (~0.05 mm).

## Relationships

- A **Plate** owns 1+ **Patches**
- A **Plate** is assigned exactly one **Pigment**
- A **Block** carries 1+ **Plates**
- Multiple **Plates** with the same **Pigment** may be consolidated into one **Plate** with multiple **Patches** (the "3 reds → 1" merge)
- Multiple **Plates** with different **Pigments** may share one **Block** if their patches are clearly/visibly apart (mask-print packing, traditional 1-block-2-color)

## Flagged ambiguities

- **"Ink" was used early in conversation** — resolved: this is mokuhanga water-based pigment. Use "Pigment" everywhere.
- **"Plate" had two meanings** (color region vs wood piece) — resolved: Plate = color region, Block = wood piece.
- **"3 reds → 1" interpretation** — resolved: one plate with multiple patches (true merge), not separate plates sharing a pigment recipe.

## Locked decisions (2026-05-08)

**Identity**
- Domain: `editor.reidsurmeier.wtf`
- Repo: new GitHub repo `editor-reidsurmeier-wtf` (separate from cnc + color-sep)
- Auth: public
- Single-user with localStorage state

**Compute & stack**
- Architecture: split — Next.js 16 frontend + FastAPI backend (server-side compute for plate-merge clustering, ghost-detail erosion, K-M K/S math)
- Frontend: Next.js 16 + Tailwind + shadcn/ui + @texel/color (OKLCH) + clipper2-js (preview-only) + Zustand
- Backend: FastAPI + numpy + pyclipr (clipper2 binding) + simplification (Visvalingam-Whyatt) + colour-science + Pillow + JSZip-equivalent (zipfile stdlib)
- Pigment math: spectral.js on frontend for swatch readout, server-side K-M (manual implementation) for export-quality composite

**Pipeline (MVP "Slim")**
- ZIP roundtrip from color-sep schema (preserved bit-for-bit, `editor.*` extension fields in manifest)
- Plate-merge auto-suggest: complete-linkage agglomerative on OKLab, coverage-weighted, ΔE2000-gated (default 6, threshold slider exposes 3/6/10), Jaccard spatial-overlap gate
- Ghost-detail filter: clipper2 Minkowski erosion at tool radius + area threshold + Visvalingam-Whyatt simplify (simplify FIRST, filter second)
- Suggestions list + drag-drop merge
- ZIP export

**Pipeline (Phase 2)**
- Underprint expansion: greedy lowest-opacity-first, K-M composite test per pixel, registration-derived choke
- Block packing: maxrects-packer, mask-print conditional on visible separation (≥30 mm slider default), kento as phantom plates
- OKLCH color popover w/ live re-recolor
- Spectral.js GLSL shader for live composite

**Modes & defaults**
- Hand mode: aggressive merge, trap 0.25 mm, registration tolerance 0.3–0.5 mm
- CNC mode: permissive merge, trap 0.05 mm or skip, registration tolerance <0.1 mm
- Print order: light→dark only (MVP), auto-assigned by lightness, drag-reorderable
- Underprint ε default: 0.5 ΔE2000 (safe)
- Mask-print "clearly apart" threshold: 30 mm default, slider 10–60 mm

**Pigment palette**
- Hardcoded mokuhanga preset: sumi (α 0.94), gofun (α 0.88), bengala (α 0.82), vermillion (α 0.85), indigo (α 0.60), gamboge (α 0.52)
- User can clone, edit α, add custom pigments

**UX**
- Single page with panel reorganization (no wizard, no tabs at top — block-view = toggle inside main canvas)
- Stack panel left, composite center, details right (matches earlier wireframe)
- Plate-merge: suggestions list (inline, one-click accept) + drag-drop (Phase 2: multi-select+M shortcut)
- Ghost vis: red fill overlay, on by default
- History: linear named snapshots (Procreate-style), auto-snapshot before any merge
- Wasted-area stat: prominent toolbar — "12 plates → N blocks · X% wood utilization"

**State & save**
- localStorage with auto-save every 30s + explicit Save/Load
- Save format: reference + delta (original ZIP hash + edit log; prompt user for ZIP if missing on reload)

**CNC handoff**
- MVP: download ZIP, manually upload to cnc.reidsurmeier.wtf
- Phase 2: direct URL handoff via R2 presigned

**Out of scope (MVP and Phase 2)**
- Bokashi simulator — surface as guidance text only
- Multi-user accounts
- Telemetry / analytics
- Iframe-embedded CNC tool
- Polygon nesting (SVGnest) — Phase 3 if wood waste becomes painful
- Reverse-direction print order (dark→light opaque) — Phase 3
