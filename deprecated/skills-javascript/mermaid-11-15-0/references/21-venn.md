# Venn Diagrams

Venn diagrams show set relationships using overlapping circles.

## Declaration

```mermaid
venn-beta
  set A
  set B
  union A,B
```

## Basic Venn Diagram

Define sets and their intersections with `union`.

```mermaid
venn-beta
  title "Team Overlap"
  set Frontend
  set Backend
  union Frontend,Backend["APIs"]
```

## Labeled Sets

Use bracket syntax for display labels.

```mermaid
venn-beta
  set A["Alpha Group"]
  set B["Beta Group"]
  union A,B["Shared"]
```

## Sized Sets

Add `:N` suffix to control circle size.

```mermaid
venn-beta
  set A["Large Set"]:20
  set B["Small Set"]:12
  union A,B["Overlap"]:3
```

## Three Sets

Define three overlapping sets.

```mermaid
venn-beta
  title "Set Relationships"
  set X
  set Y
  set Z
  union X,Y["XY"]
  union Y,Z["YZ"]
  union X,Z["XZ"]
  union X,Y,Z["XYZ"]
```
