# Wardley maps

Keyword: `wardley-beta` (beta). Positions components along Visibility (y, 0=infrastructure … 1=user-facing) and Evolution (x, 0=genesis … 1=commodity/utility).

Sources: `docs/syntax/wardley.md` at mermaid@12.3.0.

## Syntax

- `title <text>` optional; `size [w, h]` optional (default `[1100, 600]`).
- Coordinates are `[visibility, evolution]` — **opposite** of typical (x, y) notation.
- `component Name [v, e]` — optional `label [dx, dy]` offset and `(decorator)` suffix. Names may contain hyphens unquoted; quote only when needed.
- `anchor Name [v, e]` — an anchor (non-component reference point).
- `A -> B` — value-chain link.
- `evolve Name <target>` — evolution arrow to a target evolution value.
- `note "text" [v, e]` — annotation.

```mermaid
wardley-beta
title Tea Shop Value Chain

anchor Business [0.95, 0.63]
component Cup of Tea [0.79, 0.61]
component Tea [0.63, 0.81]
component Hot Water [0.52, 0.80]
component Kettle [0.43, 0.35]
component Power [0.10, 0.70]

Business -> Cup of Tea
Cup of Tea -> Tea
Cup of Tea -> Hot Water
Hot Water -> Kettle
Kettle -> Power

evolve Kettle 0.62
evolve Power 0.89

note "Standardising power allows Kettles to evolve faster" [0.30, 0.49]
```

## Gotchas

- First coordinate is visibility (vertical), second is evolution (horizontal) — easy to swap.
- Custom evolution stages and pipeline components are supported (all-examples "Wardley Maps" section has verified blocks).
