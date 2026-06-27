# Quadrant Charts

Quadrant charts plot data points on a 2D grid divided into four regions.

## Declaration

```mermaid
quadrantChart
    title Sample
    x-axis Low --> High
    y-axis Low --> High
    quadrant-1 Expand
    quadrant-2 Promote
    quadrant-3 Re-evaluate
    quadrant-4 Improve
    A: [0.3, 0.6]
```

## Basic Quadrant Chart

Define axes, quadrants, and data points (x, y in range 0–1).

```mermaid
quadrantChart
    title Campaign Analysis
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
```

## With Config and Theme

Use YAML frontmatter for chart dimensions and theme variables.

```mermaid
---
config:
  quadrantChart:
    chartWidth: 400
    chartHeight: 400
  themeVariables:
    quadrant1TextFill: "ff0000"
---
quadrantChart
    title Risk vs Impact
    x-axis Low Risk --> High Risk
    y-axis Low Impact --> High Impact
    quadrant-1 Critical
    quadrant-2 Monitor
    quadrant-3 Watch
    quadrant-4 Accept
    Issue A: [0.8, 0.9]
    Issue B: [0.2, 0.3]
    Issue C: [0.5, 0.7]
```
