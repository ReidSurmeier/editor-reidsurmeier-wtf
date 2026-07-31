# Plate Editor domain

The planned `editor.reidsurmeier.wtf` tool sits between Color Separator ZIP
export and CNC preparation. Its purpose is to consolidate related plate
geometry, remove detail that cannot be milled, and export a contract-compatible
ZIP for water-based pigment woodblock printing.

## Language

**Plate**:
One pigment and its mask. A plate may contain multiple disconnected patches.
Avoid: screen, layer, or color when referring to this domain object.

**Block**:
One physical piece of carved wood carrying one or more plates, together with
stock, grain, and registration constraints.
Avoid: plate when referring to the physical wood.

**Patch**:
One connected region within a plate. A plate owns one or more patches.

**Pigment**:
The water-based printing material assigned to a plate. It may be a single
pigment or a mixed recipe with nori paste.
Avoid: ink.

**Trap**:
A small overlap between adjacent plates that hides registration error.

**Choke**:
An inward offset of a plate edge.

**Spread**:
An outward offset of a plate edge.

**Underprint**:
An extension of a lower plate into an area covered by a later plate, constrained
by the visible composite.
Avoid: underbase.

**Hand mode**:
A printing mode designed for hand carving or baren printing, with larger
registration tolerance and trap defaults.

**CNC mode**:
A printing mode designed for machine-milled blocks, with tighter registration
tolerance and smaller trap defaults.

**Source Contract**:
The versioned ZIP and manifest accepted from the current Color Separator
exporter.

**Handoff Contract**:
The versioned ZIP and geometry requirements accepted by the current CNC
consumer.

**Historical Plan**:
A May 2026 design or implementation proposal preserved as research evidence.
It does not prove current source, dependency, service, DNS, or deployment
state.

## Relationships

- A **Plate** owns one or more **Patches**.
- A **Plate** is assigned exactly one **Pigment**.
- A **Block** carries one or more **Plates**.
- Multiple plates using the same pigment may be consolidated into one plate
  with multiple patches.
- The editor must preserve the **Source Contract** while producing a valid
  **Handoff Contract**.
- A **Historical Plan** may guide discovery but cannot override a current
  fixture-backed contract or accepted ADR.

## Current boundary

There is no implementation or deployment. The preserved plan proposed a
public, single-user editor and a split frontend/backend architecture, but those
choices must be revalidated against current upstream and downstream contracts
before implementation begins.
