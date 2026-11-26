# Radar Charts

Radar (spider) charts plot multiple variables on axes radiating from a center point.

## Declaration

```mermaid
radar-beta
    axis A, B, C
    curve c1{1, 2, 3}
```

## Basic Radar Chart

Define axes with labels and curves with data values.

```mermaid
radar-beta
    title Skills Assessment
    axis js["JavaScript"], py["Python"], sql["SQL"]
    axis devops["DevOps"], design["Design"]
    curve skills{9, 7, 8, 6, 5}
```

## Multiple Curves

Add multiple curves for comparison.

```mermaid
radar-beta
    title Team Comparison
    axis speed["Speed"], quality["Quality"], cost["Cost"], reliability["Reliability"]
    curve Alice{8, 7, 6, 9}
    curve Bob{6, 9, 8, 7}
```

## Custom Scale and Graticule

Set `min`, `max`, `ticks`, and graticule style.

```mermaid
radar-beta
    title Performance Metrics
    axis cpu["CPU"], mem["Memory"], disk["Disk"], net["Network"]
    curve metrics{75, 60, 45, 85}
    min 0
    max 100
    ticks 5
    graticule polygon
```
