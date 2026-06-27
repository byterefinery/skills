# Wardley Maps

Wardley maps visualize business strategy by positioning components along visibility and evolution axes.

## Declaration

```mermaid
wardley-beta
title Sample Map
component A [0.5, 0.5]
```

## Basic Wardley Map

Place components with `[visibility, evolution]` coordinates (both 0–1).

```mermaid
wardley-beta
title Tea Shop Value Chain
anchor Business [0.95, 0.63]
component CupOfTea [0.79, 0.61]
component Tea [0.63, 0.81]
component HotWater [0.52, 0.80]
component Kettle [0.43, 0.35]
component Power [0.10, 0.70]
Business -> CupOfTea
CupOfTea -> Tea
CupOfTea -> HotWater
HotWater -> Kettle
Kettle -> Power
```

## With Evolution and Notes

Use `evolve` to show component movement. Add `note` for annotations.

```mermaid
wardley-beta
title E-Commerce Platform
anchor Customer [0.9, 0.5]
component Website [0.8, 0.4]
component Hosting [0.5, 0.7]
component Internet [0.2, 0.9]
Customer -> Website
Website -> Hosting
Hosting -> Internet
evolve Hosting 0.85
note "Hosting is becoming commoditized" [0.4, 0.6]
```

## Size and Labels

Set canvas size with `size [width, height]`. Label components with bracket syntax.

```mermaid
wardley-beta
title Software Supply Chain
size [1100, 600]
anchor UserNeed [0.95, 0.5]
component App [0.8, 0.3]
component Framework [0.6, 0.6]
component Cloud [0.3, 0.85]
component Electricity [0.1, 0.95]
UserNeed -> App
App -> Framework
Framework -> Cloud
Cloud -> Electricity
```
