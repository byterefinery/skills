# Cynefin framework diagrams

Keyword: `cynefin-beta` (beta, v11.16.0+). Sense-making map across five complexity domains: Clear (best practices), Complicated (good practices), Complex (emergent practices), Chaotic (novel practices), Confusion/Disorder (move items out).

Sources: `docs/syntax/cynefin.md` at mermaid@12.3.0.

## Syntax

- `title <text>` optional.
- Domain blocks: `complex`, `complicated`, `clear`, `chaotic`, `confusion` — each opens a block of quoted item labels on their own lines.
- Transitions at top level: `<domain1> --> <domain2> : "label"`.

```mermaid
cynefin-beta
  title Incident Response

  complex
    "Investigate root cause"
    "Run chaos experiment"

  complicated
    "Analyze performance data"
    "Expert review needed"

  clear
    "Restart service"
    "Apply known fix"

  chaotic
    "Page on-call immediately"

  confusion
    "Unknown failure mode"
```

With transitions (docs):

```mermaid
cynefin-beta
  title Strategy Categorization

  complex
    "Market research"

  complicated
    "Competitive analysis"

  clear
    "Standard pricing"

  chaotic
    "Crisis management"

  complex --> complicated : "Pattern identified"
  complicated --> clear : "Best practice codified"
  clear --> chaotic : "Complacency"
  chaotic --> complex : "Stabilized"
```

## Gotchas

- Items are quoted strings, one per line, inside a domain block.
- Keep per-domain lists short — quadrant domains don't clip (visual overflow), and the confusion ellipse caps at three items showing a `+N more` badge.
- Domains render even with no items (useful as a worksheet template).
