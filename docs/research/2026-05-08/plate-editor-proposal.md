# Plate Editor — Architecture Proposal

**Position:** sits between `color.reidsurmeier.wtf` (color-separator) and `cnc.reidsurmeier.wtf` (CNC tool).

**Working name:** `press.reidsurmeier.wtf` (alternatives: `plates`, `studio`, `consolidate`)

**Date:** 2026-05-07

---

## 1. The 5 pain points → solutions

| Pain | Solution | Library/algorithm |
|------|----------|-------------------|
| Ghost CNC detail on un-millable features | Tool-radius Minkowski erosion + area threshold + path simplify, BEFORE handoff to CNC | clipper2-js + Visvalingam-Whyatt |
| Pigment-realistic color mixing | spectral.js (MIT, 38-ch K-M, GLSL shader, tinting strength) — NOT mixbox (CC BY-NC) | spectral.js |
| OKLCH picker w/ live composite | shadcn Popover + sliders, gamut-mapped via @texel/color, WebGL2 composite re-render | @texel/color |
| Auto-merge similar plates (3 reds → 1) | Complete-linkage agglomerative clustering on OKLab centroids, coverage-weighted, ΔE2000-gated, Jaccard spatial-overlap gate | hclust + culori (or hand-rolled) |
| General plate editor UX | Stack-primary layer panel (Procreate-like), 3 merge paths, named snapshots history, mode toggle (hand-print vs CNC) | Next.js 16 + shadcn/ui + Tailwind |

---

## 2. Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Framework | Next.js 16 (App Router) | matches existing sites, SSG for marketing, server route for ZIP processing |
| UI | shadcn/ui + Tailwind v4 | matches house style, ~80% coverage |
| Color engine | @texel/color | 3.5 KB, ~125× faster than colorjs, Ottosson cusp gamut map |
| Pigment engine | spectral.js (MIT) | 38-channel K-M, GLSL shader, tinting strength, no commercial gate |
| Polygon ops | clipper2-js | Vatti, handles potrace self-intersections (martinez breaks) |
| Path simplify | Visvalingam-Whyatt | preserves visual character at woodblock scale |
| Bitmap morph | OpenCV.js | only when input is PNG mask, for opening/closing |
| ZIP I/O | JSZip | matches cnc tool's existing usage |
| State | Zustand or React state | linear history with named snapshots |
| Live preview | WebGL2 canvas | spectral.js GLSL fragment shader |
| Service | systemd user unit on Linux server | matches existing deploy pattern |
| Deploy | port 3007 + Cloudflare tunnel | matches existing pattern |

---

## 3. Data flow

```
[color.reidsurmeier.wtf]                        [cnc.reidsurmeier.wtf]
  ZIP { composite.png,                            ZIP { 1_xxxxxx.svg,
        png/N_xxxxxx.png,         ┌────►          2_xxxxxx.svg,
        svg/N_xxxxxx.svg,         │               manifest.json,
        manifest.json }           │               composite.png }
        │                         │                       ▲
        ▼                         │                       │
  ┌─────────────────────────────────────────────┐         │
  │           press.reidsurmeier.wtf            │         │
  │                                             │         │
  │  IMPORT      EDIT         EXPORT            │─────────┘
  │  ──────      ────         ──────            │
  │  • ZIP       • merge      • ZIP (same       │
  │  • URL       • recolor      schema)         │
  │  • S3 ref    • filter     • direct handoff  │
  │              • reorder      via R2 + URL    │
  │                                             │
  └─────────────────────────────────────────────┘
```

**Schema preservation:** export ZIP MUST match color-separator's schema bit-for-bit so cnc tool ingests unchanged. New fields go in `manifest.json` extension namespace (`press.*`).

---

## 4. Pipeline (per-plate)

```
1. Ingest:       parse manifest.json + load PNG masks + SVG paths
2. Augment:      compute OKLab centroid, coverage %, dilated-mask Jaccard graph
3. Simplify:     Visvalingam-Whyatt (default ε=0.5 px)        ── pain #1 step 1
4. Filter:       clipper2 inset by tool_r, drop A < 17.8 mm² ── pain #1 step 2
5. Mode-gate:    hand-print → aggressive merge / CNC → permissive
6. Suggest:      complete-linkage cluster on weighted-OKLab   ── pain #4
                 cut at ΔE2000 ≤ 6 (default), Jaccard gate
7. Apply:        user-confirmed merges → recolor via spectral ── pain #2
8. Recolor:      OKLCH picker → spectral-mix from palette     ── pain #3
9. Composite:    WebGL2 shader, light→dark stack order
10. Export:      ZIP w/ same schema → handoff URL to cnc
```

---

## 5. UI layout (3-pane)

```
┌───────────────────────────────────────────────────────────────────┐
│  press.reidsurmeier.wtf       hand-print | CNC      [export ▼]    │
├──────────────┬──────────────────────────────┬─────────────────────┤
│ PLATES       │                              │ DETAILS             │
│              │                              │                     │
│ [eye] swatch │      composite preview       │ Plate: red_dc2828   │
│   plate_01   │      (WebGL2 canvas,         │ Coverage: 14.2%     │
│   12.3% ─── │       solo on cmd-click,     │ ΔE to nearest: 4.1  │
│              │       red overlay = ghost)   │                     │
│ [eye] swatch │                              │ Color popover ▼     │
│   plate_02   │                              │ ┌─────────────────┐ │
│   8.4%  ──── │                              │ │ OKLCH sliders   │ │
│              │                              │ │ L 0.62          │ │
│ [eye] swatch │                              │ │ C 0.18          │ │
│   plate_03   │                              │ │ H 28°           │ │
│   ...        │                              │ │                 │ │
│              │                              │ │ Mix readout:    │ │
│ Suggestions  │                              │ │ Cad Red 0.31    │ │
│ ───────────  │                              │ │ Burnt Sienna .69│ │
│ Merge 1+3    │                              │ └─────────────────┘ │
│ ΔE 3.8  [✓]  │                              │                     │
│              │                              │ [history ▼]         │
└──────────────┴──────────────────────────────┴─────────────────────┘
```

Merge paths:
- **Drag plate row onto another row** → merge dialog
- **Multi-select rows + press M** → merge dialog
- **Click suggestion** → one-tap accept

---

## 6. MVP vs full scope

### MVP (week 1-2 — ship to color.reidsurmeier.wtf workflow)
1. ZIP import from color-sep
2. Stack panel with eye/solo, color swatch, coverage %
3. Auto-merge suggestions (complete-linkage, ΔE2000 ≤ 6, Jaccard gate)
4. One-click merge accept
5. ZIP export (same schema)
6. **Ghost-detail filter (clipper2 erosion + area threshold) — solves the actual production blocker**

### Phase 2 (week 3-4)
7. OKLCH popover w/ @texel/color
8. spectral.js mix readout (read-only — show what pigments approximate the picked color)
9. Live composite preview WebGL canvas
10. Mode toggle (hand-print / CNC)

### Phase 3 (week 5+)
11. Direct handoff URL → cnc.reidsurmeier.wtf (R2 presigned + auto-redirect)
12. Spectral.js full per-pixel layering on GPU
13. Bokashi simulator (gradient-replace 2 plates → 1 plate)
14. Mokuhanga preset (named-pigment palette)
15. Print order reorder (light→dark default)
16. Linear history with named snapshots

### Out of scope
- Node graph editor (overkill, defer)
- AI auto-recolor (defer)
- Bit/V-bit per-pass calculator (CNC tool's job)

---

## 7. Key constraints

1. **Full resolution preserved** — no downscale (existing project policy)
2. **Kento marks pass through unchanged** — never touch them
3. **Schema-compatible export** — cnc tool ingests without modification
4. **OSS-direction licensing** — spectral.js (MIT), not mixbox (CC BY-NC)
5. **Light→dark print order** — reflect mokuhanga tradition in default plate stack
6. **Mode-aware defaults** — hand-print vs CNC have different merge aggressiveness

---

## 8. Open questions for grilling

1. Project name: `press`, `plates`, `studio`, `consolidate`, `inkstack`, ...?
2. Public or auth-gated like kg? (Likely auth — woodblock workflow is personal)
3. Save state: per-user account or stateless URL-import flow?
4. New repo on GitHub or monorepo with cnc tool?
5. Phase 2 vs ship MVP and iterate from real woodblock prints?
6. Spectral.js GLSL shader — eat the WebGL2 complexity or use canvas-pixel sRGB approximation in MVP?
7. Bokashi simulator — pain point not in original list, but tradition specialist flagged as plate-merge alternative. Worth Phase 3?
8. Direct handoff — push to cnc via R2 + URL? Or download-then-upload manual?

---

## 9. Estimated effort

- MVP: 4-6 specialist-days (Frontend + clipper2 wiring + cluster algo + ZIP roundtrip)
- Phase 2: +3-4 days (OKLCH + spectral.js + WebGL canvas)
- Phase 3: +5-7 days (handoff, full GPU layering, bokashi, history)

**Total:** ~12-17 specialist-days for full vision. MVP unblocks the production workflow.
