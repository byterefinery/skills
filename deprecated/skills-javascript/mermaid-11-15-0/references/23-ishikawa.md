# Ishikawa (Fishbone) Diagrams

Ishikawa diagrams visualize cause-and-effect relationships, with the problem at the head and causes branching from the spine.

## Declaration

```mermaid
ishikawa-beta
    Problem
    Cause Category
        Sub-cause 1
        Sub-cause 2
```

## Basic Fishbone

Define the problem (first line) and cause categories with indented sub-causes.

```mermaid
ishikawa-beta
    Blurry Photo
    Process
        Out of focus
        Shutter speed too slow
    User
        Shaky hands
    Equipment
        Dirty lens
        Damaged sensor
    Environment
        Too dark
        Subject moved
```

## Deeply Nested Causes

Nest causes multiple levels deep.

```mermaid
ishikawa-beta
    Server Downtime
    Hardware
        Disk
            Bad sectors
            Full capacity
        Memory
            Leak
            Insufficient RAM
    Software
        Bug in release v2.1
        Misconfigured firewall
    Human
        Deployment error
        Missing monitoring alerts
```

## With Many Categories

Use multiple cause categories for comprehensive analysis.

```mermaid
ishikawa-beta
    Late Delivery
    Logistics
        Traffic delays
        Wrong address
    Warehouse
        Picking errors
        Packaging delay
    Supplier
        Late raw materials
        Quality issues
    Planning
        Unrealistic deadlines
        Resource shortage
```
