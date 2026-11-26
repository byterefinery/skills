# Treemap Diagrams

Treemaps display hierarchical data as nested rectangles, sized proportionally to values.

## Declaration

```mermaid
treemap-beta
"Root"
    "Child": 10
```

## Basic Treemap

Define parent sections and leaf nodes with values.

```mermaid
treemap-beta
"Category A"
    "Item A1": 10
    "Item A2": 20
"Category B"
    "Item B1": 15
    "Item B2": 25
```

## Hierarchical Treemap

Nest multiple levels deep.

```mermaid
treemap-beta
"Products"
    "Electronics"
        "Phones": 50
        "Computers": 30
        "Accessories": 20
    "Clothing"
        "Shirts": 15
        "Pants": 10
    "Food"
        "Snacks": 8
        "Drinks": 12
```

## With Styling

Use `:::class` inline on nodes and `classDef` after the diagram.

```mermaid
treemap-beta
"Disk Usage"
    "System": 40:::sys
    "Users": 25
    "Apps": 20
    "Temp": 15
classDef sys fill:#e74c3c,color:#fff
```
