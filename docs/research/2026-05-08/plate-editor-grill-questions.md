# Plate Editor — Grill Questions

**Date:** 2026-05-07
**Project working name:** TBD (`press` / `plates` / `studio` / `consolidate` / `inkstack` / `between`)
**Position:** sits between `color.reidsurmeier.wtf` (color-separator) and `cnc.reidsurmeier.wtf` (CNC milling)
**Format:** one question per decision, with my recommended answer + the trade-off

---

## Already locked (in this conversation)

- ✅ **Print order:** mokuhanga light→dark (drives expansion direction, lowest-opacity-first greedy)
- ✅ **Block packing default — mask-print conditional:** only applies when regions are clearly/visibly apart (matches traditional 1-block-2-color carving). Need to define "clearly apart" precisely (Q17 below).
- ✅ **Pigment engine:** spectral.js (MIT) — NOT mixbox (CC BY-NC paid commercial)
- ✅ **Color engine:** @texel/color (3.5KB, ~125× faster than colorjs)
- ✅ **Polygon ops:** clipper2-js (Vatti — handles potrace self-intersections)
- ✅ **Path simplify:** Visvalingam-Whyatt (preserves visual character vs RDP)
- ✅ **Block packing lib:** maxrects-packer Phase 1, SVGnest port Phase 2
- ✅ **Plate-merge algorithm:** complete-linkage agglomerative on OKLab, coverage-weighted, ΔE2000-gated, Jaccard spatial-overlap gate (touching plates merge eagerly)
- ✅ **Schema:** export ZIP matches color-sep schema bit-for-bit; new fields under `press.*` namespace in manifest

---

## Domain language

### Q1: Disambiguate "plate"

We've been using "plate" two ways. Lock the distinction:

| Term | Meaning |
|------|---------|
| **Plate** | one ink + its mask (one color, may have multiple non-touching patches). Logical thing color-sep emits. |
| **Block** | one physical piece of carved wood. Carries 1+ plates. Has stock size, grain, kento. |
| **Patch** | one connected region within a plate. A plate has ≥1 patches. |
| **Ink** | the pigment/color recipe assigned to a plate. May be shared across plates after consolidation. |

Avoid: "screen", "layer", "color" (too generic).

**Sub-question 1a:** "3 reds → 1" means:
- (a) one plate with 3 patches (true merge, lose plate identity)
- (b) one ink shared across 3 plates that block-pack together

**My rec:** (a). Simpler model, matches screenprint color-reduction idiom, matches user's natural language.

### Q2: Adopt screenprint vocabulary or invent ours?

Screenprint terms research surfaced:
- **trap / choke / spread** — overlap/inset to hide misregistration
- **under-base white** — opaque foundation under colors
- **ganged screens** — multiple colors per screen frame

**My rec:** adopt **trap** + **choke** (industry-standard, well-understood) but rename **under-base** → **underprint** (matches user's natural language, fits mokuhanga semantics: under-printing under darker translucents, not under colors over a dark substrate).

### Q3: Mode names

The proposal has a "hand-print vs CNC" toggle that affects merge aggressiveness, choke value, and registration tolerance.

Options:
- (a) **Hand / CNC** — clear, current
- (b) **Wood / Machine** — broader (covers linocut hand-cut)
- (c) **Press / Mill** — verb-based

**My rec:** (a) "Hand" / "CNC" — ships the simplest mental model for now. Renamable later.

---

## Identity / scoping

### Q4: Project name

Candidates:
- **press** — verb-anchored, links to physical action, short URL `press.reidsurmeier.wtf`
- **plates** — describes contents but ambiguous after Q1's terminology lock
- **studio** — generic; conflicts with screen-print "Sep Studio"
- **consolidate** — describes one feature, not the whole thing
- **inkstack** — accurate but jargon
- **between** — clever (positioning), maybe too clever
- **kento** — Japanese registration mark, evocative, short
- **bangi** — 板木, "block wood", traditional term

**My rec:** **`press`** if you want it to feel like a tool, **`kento`** if you want it to feel like a craft. Both are short, both available.

### Q5: Repo strategy

- (a) **New repo** `press-reidsurmeier-wtf` (separate from cnc tool)
- (b) **Monorepo** with cnc tool — `apps/press` + `apps/cnc` + shared `packages/plate-types`
- (c) **Pull cnc into press** as a vertical (cnc becomes a tab/page inside the editor)

**My rec:** (a) for speed. Monorepo wins if data contract churns; we expect ZIP schema stable since color-sep is the upstream source. Move to monorepo only if shared types start fragmenting.

### Q6: Auth model

- (a) **Auth-gated** like kg.reidsurmeier.wtf (basic auth via Cloudflare Access)
- (b) **Public** like color-sep
- (c) **No auth, unguessable URL** for in-progress projects

**My rec:** (a) basic auth. Plate editing is personal craft work, no need to expose. Cheap to add via existing CF tunnel.

### Q7: Single-user vs product

- (a) **Single user** (you only). No accounts. State is per-browser localStorage.
- (b) **Multi-user** — accounts, project save, share links.

**My rec:** (a). Build for one customer first. Don't add multi-user complexity until another printmaker wants it.

### Q8: Browser-only or server-side processing?

4096² composites, K-M shader passes, mask Boolean ops are heavy.
- (a) **Browser-only** — WebGL2 + Web Workers, runs on user's GPU
- (b) **Server-side** — FastAPI backend like color-sep, returns processed ZIP
- (c) **Hybrid** — browser for live edit, server for final export with full-quality compositing

**My rec:** (a) for MVP. WebGL2 is enough for woodblock-scale projects (typically <20 plates, <8K canvas). Falls back to canvas approximation if no WebGL2. Add (c) if/when needed.

### Q9: State persistence

- (a) **Stateless URL flow** — drop in a ZIP from color-sep, edit, export ZIP, browser forgets.
- (b) **localStorage project save** — auto-save in-progress edits per browser
- (c) **Account-bound projects** — saved server-side

**My rec:** (b) localStorage with explicit "save project" / "load project" buttons + auto-save every 30s. Ships fast, recovers from accidental refresh, matches single-user assumption.

---

## Scope / MVP

### Q10: MVP cut

- **Slim (week 1-2):** ZIP roundtrip + plate-merge auto-suggest + ghost-detail filter
- **Core (week 1-3):** Slim + underprint expansion + block packing (mask-print conditional)
- **Full Phase 1 (week 1-4):** Core + OKLCH popover + spectral.js read-only mix readout

**My rec:** **Slim**. Three reasons:
1. Solves the PRODUCTION blocker fastest (ghost detail + plate consolidation are top pain).
2. Underprint expansion is an unproven idea in your workflow — print test slim output before committing engineering to underprint math.
3. Building block packing requires sample real-world projects to tune cost-function weights; you don't have those yet.

Then iterate Core/Phase1 on real prints.

### Q11: Bokashi simulator

Tradition-specialist found bokashi gradient can replace 2-3 close plates.
- (a) Skip entirely — bokashi is hand-print only, doesn't translate to CNC
- (b) Phase 3 feature — gradient SVG generator with 2-color stops
- (c) MVP feature — propose-bokashi when 2 close plates have spatial gradient axis

**My rec:** (a) skip. Bokashi requires brush+water on a real woodblock; CNC mills can't reproduce the gradient. Surface only as guidance text: "These 2 plates could be one bokashi block in hand printing."

### Q12: Direct handoff to cnc tool

- (a) **Download ZIP, manually upload to cnc.reidsurmeier.wtf** — current pattern
- (b) **Direct URL handoff** — press POSTs ZIP to R2, returns presigned URL, cnc tool reads it
- (c) **Iframe embed cnc tool inside press** — full single-page experience

**My rec:** (a) MVP, (b) Phase 2. Iframe (c) is fragile, drops state on refresh, hard to debug.

### Q13: Wasted-area stat

Block-packing research recommends a "blocks vs plates" + "wood utilization %" badge.
- (a) Yes, prominent toolbar stat
- (b) Tucked in details panel
- (c) No

**My rec:** (a). The whole product is "fewer blocks, less wood" — make the win visible.

---

## Technical defaults

### Q14: Underprint expansion ε default (ΔE2000)

- **safe = 0.5** — below perceptibility, safest under viewing variance
- **default = 1.0** — JND, "imperceptible" by definition
- **aggressive = 2.0** — perceptible direct A/B but not standalone

**My rec:** **0.5 (safe) shipped as default**. Reason: woodblock viewers look closely. ΔE2000 < 1 is computed under controlled lighting; gallery lighting expands variance. Conservatism wins. Slider exposes 0.5/1.0/2.0.

### Q15: Trap/choke value defaulting

- (a) **Auto by mode**: Hand mode = 0.25mm choke (registration ~0.3-0.5mm). CNC mode = 0.05mm or skip (registration <0.1mm).
- (b) **User sets per project**
- (c) **Fixed default** with override

**My rec:** (a) auto by mode + user override per project. Trap is a registration-tolerance derivative — auto-deriving from mode matches industry practice.

### Q16: WebGL2 spectral shader day 1?

- (a) **WebGL2 K-M shader from MVP** — 36-bin reflectance, full-quality composite preview
- (b) **sRGB-α canvas approximation in MVP**, upgrade to WebGL2 in Phase 2

**My rec:** (b). MVP needs to ship. sRGB-α is wrong for translucent inks but adequate as a thumbnail. The WebGL2 shader is its own engineering project (~3 days alone). Don't gate MVP on it.

Trade-off: composite preview will be visibly off for very translucent inks (gamboge over indigo) until upgrade. Live with it; flag with a banner: "approximate preview — print test for true color".

### Q17: Mokuhanga pigment palette

- (a) **Ship hardcoded mokuhanga preset** with 6 verified pigments (sumi, gofun, bengala, vermillion, indigo, gamboge) and their α values
- (b) **Custom palette only** — user adds their own swatches with α
- (c) **Both — preset as starting point, fully editable**

**My rec:** (c). Hardcoded preset ships immediately and makes the tool feel knowledgeable. User edits the palette to match their actual ink jars (different brands have different α). Add/remove/clone swatches.

### Q18: Define "clearly apart" for mask-print packing

User clarified: mask-print only when regions are visibly separated. Need a threshold.

- (a) **Visual gap ≥ N mm** (concrete: ≥25mm from packing research, ≥50mm safer)
- (b) **No bounding-box overlap + center-distance threshold**
- (c) **User-tunable slider** with default ≥30mm

**My rec:** (c) slider, default 30mm. Surface as "Mask-print separation: 30mm" in the block-pack mode panel. Below threshold = same-ink only. Above = different-ink allowed on same block.

### Q19: Print order — editable?

Mokuhanga light→dark is the rule, but real printmakers sometimes break it.
- (a) **Auto-assigned by lightness, locked**
- (b) **Auto-assigned, user can reorder by drag**
- (c) **No default, user always sets**

**My rec:** (b) auto + drag-reorder. Default is right 95% of the time; print order matters for underprint expansion direction.

### Q20: Print order direction toggle

Some woodblock workflows use opaque inks (gofun-style) and print dark→light (light covers dark).
- (a) Single direction, light→dark only
- (b) Mode toggle: light→dark (translucent) vs dark→light (opaque)

**My rec:** (a) for MVP. (b) is a Phase 3 expansion. Most modern mokuhanga is translucent; opaque-only is a niche.

---

## UX details

### Q21: Plate-merge interaction paths

UX-specialist recommended 3 paths: drag-drop, multi-select+M, suggestions list.
- (a) Ship all 3
- (b) Ship just suggestions list (lowest UX risk)
- (c) Ship suggestions + drag-drop

**My rec:** (c). Multi-select+M is power-user; ship after watching real usage. Drag-drop is intuitive and matches Photoshop layer panel.

### Q22: History model

- (a) **Linear with named snapshots** (Procreate-style)
- (b) **Tree branching history** (Git-like)
- (c) **Linear, unnamed**, just undo/redo

**My rec:** (a) linear named snapshots. Tree is overkill — confirmed by UX-specialist. User wants to "try a merge, undo, try another" which works fine in linear with auto-snapshot before merge.

### Q23: Ghost-detail visualization

- (a) **Red fill overlay** on unmillable areas (Carbide Create style)
- (b) **Striped pattern** (less aggressive)
- (c) **Toggle-only** (off by default)

**My rec:** (a) red fill, on by default. The whole point is making the problem visible.

### Q24: Suggestion presentation

When auto-merge finds candidates:
- (a) Inline list at bottom of plate panel, one-click accept
- (b) Modal that pops up on import with all suggestions
- (c) Side panel, scrollable, with diff preview

**My rec:** (a) inline list. (b) interrupts. (c) too heavy. Each suggestion shows: "Plates 1 + 3 → ΔE 3.8 [✓ accept]".

---

## Open or punt

### Q25: Project save format

If we go localStorage save (Q9b):
- (a) **Full JSON** — plates, masks (base64), edits, history
- (b) **Reference + delta** — original ZIP hash + edit log
- (c) **Compact binary** (msgpack)

**My rec:** (b) reference + delta. Original ZIP is large; user keeps it on disk. We persist only what's been changed. If original ZIP is missing on reload, prompt user to drop it back in.

### Q26: Multi-page workflow vs single-page

- (a) Single page, panels reorganize for tasks
- (b) Wizard: Import → Merge → Recolor → Pack → Export
- (c) Tabs: Plates | Blocks | Composite

**My rec:** (a) single page with panel reorganization. (b) wizard is rigid. (c) is what the UX research recommended (block-view toggle); fold that into single-page.

### Q27: First user is Reid only — testing strategy

- (a) Ship to staging, you test with real recent woodblock projects
- (b) Build with synthetic test fixtures, ship after
- (c) Write Playwright + visual diff tests, then ship

**My rec:** (a). You have real projects. Synthetic fixtures will miss edge cases the real ones expose. Tests come Phase 2 once we know what shapes the data takes.

### Q28: Telemetry / observability

- (a) None — single user, no need
- (b) Sentry only for crashes
- (c) Sentry + Plausible (anonymous)

**My rec:** (a) none. Single user, single browser, no privacy mess. You'll know if it crashes (you'll be looking at it).

---

## Architecture decision records (deferred)

ADRs will be written when these decisions are reversed or when ambiguity persists. Likely first ADRs:
- **ADR-001: Pigment library = spectral.js, not mixbox** — irreversible commercial constraint
- **ADR-002: Underprint expansion = K-M composite test, not RGB-α** — math correctness, surprising to readers
- **ADR-003: Mask-print packing conditional on visible separation** — user-stated constraint, not industry standard

These will be created lazily when the topic comes up in code review or planning.

---

## Open language ambiguities (to resolve as we build)

- "Composite" — used for both (a) the visible composite preview and (b) the printed composite. Lock in code review.
- "Coverage" — % of canvas occupied by a plate. Confirm this excludes kento marks.
- "Ink" vs "color" vs "pigment" — pigment = raw material, ink = mixed working substance, color = sRGB/OKLCH coordinates. Confirm.

---

## Summary table — recommendations at a glance

| # | Decision | My rec |
|---|----------|--------|
| 1 | "plate" vs "block" terminology | Lock distinction (plate=color, block=wood) |
| 1a | 3-reds-→-1 model | (a) one plate, 3 patches |
| 2 | Vocabulary | Adopt trap/choke; rename underbase → underprint |
| 3 | Mode names | Hand / CNC |
| 4 | Project name | `press` (tool feel) or `kento` (craft feel) |
| 5 | Repo | New repo separate from cnc |
| 6 | Auth | Basic auth via CF Access |
| 7 | Multi-user | Single user only |
| 8 | Compute | Browser-only WebGL2 + workers |
| 9 | State | localStorage with save/load + auto-save |
| 10 | MVP cut | Slim (week 1-2) |
| 11 | Bokashi | Skip; surface as guidance text |
| 12 | CNC handoff | Download/upload MVP, direct URL Phase 2 |
| 13 | Wasted-area stat | Yes, prominent toolbar |
| 14 | Underprint ε default | 0.5 (safe) |
| 15 | Trap/choke value | Auto by mode + override |
| 16 | WebGL2 day 1 | No, sRGB-α MVP, upgrade Phase 2 |
| 17 | Mokuhanga palette | Hardcoded preset + fully editable |
| 18 | "Clearly apart" threshold | Slider, 30mm default |
| 19 | Print order editable | Auto + drag-reorder |
| 20 | Direction toggle | light→dark only MVP |
| 21 | Plate-merge UX | Suggestions list + drag-drop |
| 22 | History | Linear named snapshots |
| 23 | Ghost vis | Red fill, on by default |
| 24 | Suggestions | Inline list, one-click accept |
| 25 | Save format | Reference + delta |
| 26 | Layout | Single page, panel reorganization |
| 27 | Testing | Real projects on staging |
| 28 | Telemetry | None |

---

## Next step after grilling

1. User answers Q1-Q28 (or accepts/rejects recs)
2. Generate `CONTEXT.md` capturing locked terminology
3. Write ADR-001 through ADR-003 for the irreversible decisions
4. Generate proposal v3 with all decisions baked in
5. Run /to-prd or /to-issues to break into actionable build tickets
