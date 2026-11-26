# Ishikawa (fishbone) diagrams

Keyword: `ishikawa-beta` (plain `ishikawa` works too). Cause-and-effect diagrams: the first line is the event/problem; subsequent indented lines are causes; indentation builds the fishbone structure.

Sources: `docs/syntax/ishikawa.md` at mermaid@12.3.0.

## Syntax

```mermaid
ishikawa-beta
    Blurry Photo
    Process
        Out of focus
        Shutter speed too slow
        Protective film not removed
        Beautification filter applied
    User
        Shaky hands
    Equipment
        LENS
            Inappropriate lens
            Damaged lens
            Dirty lens
        SENSOR
            Damaged sensor
            Dirty sensor
    Environment
        Subject moved too quickly
        Too dark
```

Rules (from the docs):
- The first line is the event (problem) of the diagram.
- Subsequent lines are causes of the event.
- The "fishbone" structure is indicated by indentation (causes under category labels like `Process`, `User`, `Equipment`, `Environment`).

Late food delivery root causes — see all-examples "Ishikawa Diagram" section for the second verified block.
