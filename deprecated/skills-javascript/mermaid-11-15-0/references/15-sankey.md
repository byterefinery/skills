# Sankey Diagrams

Sankey diagrams visualize flows of values between nodes, with link thickness proportional to magnitude.

## Declaration

```mermaid
sankey-beta
    A,B,10
```

## Basic Sankey

List links as `Source,Target,value` per line.

```mermaid
sankey-beta
    Farm,Vegetables,50
    Farm,Meat,30
    Vegetables,Store,45
    Meat,Store,28
    Store,Customer,70
    Vegetables,Waste,5
    Meat,Waste,2
```

## With Config

Use YAML frontmatter for per-diagram settings.

```mermaid
---
config:
  sankey:
    showValues: false
---
sankey-beta
    Coal,Thermal,60
    Gas,Thermal,40
    Wind,Electricity,30
    Solar,Electricity,20
    Thermal,Grid,80
    Electricity,Grid,50
```

## Multi-Node Flows

Multiple sources and sinks with intermediate nodes.

```mermaid
sankey-beta
    Agriculture,Biofuel,120
    Agriculture,Waste,30
    Biofuel,Liquid,100
    Biofuel,Gas,20
    Waste,Solid,25
    Waste,Gas,5
    Liquid,Transport,90
    Gas,Heating,15
    Solid,Industry,20
```
