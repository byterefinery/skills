# Flowcharts

Flowcharts (and the legacy `graph` keyword) are Mermaid's most versatile diagram type. They model processes, workflows, decision trees, and system architectures.

## Declaration

```mermaid
flowchart LR
```

Direction keywords: `TB` (top-to-bottom, default), `LR` (left-to-right), `RL`, `BT`. Use `graph TD` as a legacy alternative.

## Nodes

Plain identifiers or quoted labels. Shapes wrap the label in special brackets.

```mermaid
flowchart LR
    A["Plain node"]
    B(["Rounded"])
    C[/Actor\]
    D{Diamond}
    E[(Database)]
    F[[Parallel]]
    H((Circle))
    I>Asymmetrical]
```

## Edges

`-->`, `-.->` (dotted), `-.-.` (dashed), `===` (thick). Add text with `-->|label|`. Arrowheads: `--o`, `--x`, `o--`, `x--`, `o--o`, `x--x`.

```mermaid
flowchart LR
    A-->B
    B-.->C
    C==>D
```

## Subgraphs

Group related nodes. Use `direction` to override flow inside the subgraph.

```mermaid
flowchart TB
    subgraph Cluster
        direction LR
        A-->B
        B-->C
    end
    C-->D
    D-->A
```

## Styling

Apply via `class`, `style`, or `linkStyle`. Classes are defined with `classDef`.

```mermaid
flowchart LR
    A-->B-->C
    classDef highlight fill:#f9d56e,stroke:#e67e22,stroke-width:2px
    class B highlight
    style C fill:#a8e6cf,color:#333
    linkStyle 0 stroke:#e74c3c,stroke-width:3px
```

## Conditional (if/else)

```mermaid
flowchart TD
    Start --> Condition{Is valid?}
    Condition -->|Yes| Process[Process data]
    Condition -->|No| Error[Show error]
    Process --> End[Done]
    Error --> End
```

## Direction Override Per Subgraph

```mermaid
flowchart TB
    A-->B
    subgraph LeftToRight
        direction LR
        B-->C-->D
    end
    D-->E
```
