# Quadrant charts

Keyword: `quadrantChart`.

Sources: `docs/syntax/quadrantChart.md` at mermaid@12.3.0.

## Syntax

- `title <text>`
- `x-axis <left> --> <right>` (right optional)
- `y-axis <bottom> --> <top>` (top optional)
- `quadrant-1 <text>` … `quadrant-4 <text>` — quadrant labels (1 = top-right, 2 = top-left, 3 = bottom-left, 4 = bottom-right)
- Points: `<label>: [x, y]` with x, y in 0–1.

```mermaid
quadrantChart
    title Reach and engagement of campaigns
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved
    Campaign A: [0.3, 0.6]
    Campaign B: [0.45, 0.23]
    Campaign C: [0.57, 0.69]
    Campaign D: [0.78, 0.34]
    Campaign E: [0.40, 0.34]
    Campaign F: [0.35, 0.78]
```

## Verified examples

Eisenhower matrix with styled points — see all-examples "Quadrant Chart" section for the full verified block.
