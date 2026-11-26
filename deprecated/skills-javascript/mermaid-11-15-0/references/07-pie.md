# Pie Charts

Pie charts display proportional data as slices of a circle.

## Declaration

```mermaid
pie
```

## Basic Pie Chart

Define title and slices with `: value`.

```mermaid
pie
    title Browser Usage
    "Chrome" : 45
    "Firefox" : 25
    "Safari" : 20
    "Edge" : 10
    "Other" : 10
```

## With Percentages

Values are auto-normalized to percentages. Use integers or decimals.

```mermaid
pie
    title Survey Results
    "Strongly Agree" : 35
    "Agree" : 28
    "Neutral" : 15
    "Disagree" : 12
    "Strongly Disagree" : 10
```
