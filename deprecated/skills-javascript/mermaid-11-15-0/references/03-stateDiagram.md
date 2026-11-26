# State Diagrams

State diagrams model the lifecycle of an entity through states and transitions. Use `stateDiagram-v2` for composite states, concurrency, and postconditions.

## Declaration

```mermaid
stateDiagram-v2
```

## Basic States and Transitions

States are plain identifiers or labeled with `[label]`. Transitions use `-->`. Initial and final states use `[*]`.

```mermaid
stateDiagram-v2
    [*] --> Still
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
```

## Composite (Nested) States

Group sub-states inside a named state block.

```mermaid
stateDiagram-v2
    [*] --> Plant
    state Plant {
        [*] --> Seed
        Seed --> Sprout
        Sprout --> Tree
        Tree --> [*]
    }
```

## Choice (Decision) Points

Use `choice` to model branching based on conditions.

```mermaid
stateDiagram-v2
    [*] --> IsPositive
    state IsPositive <<choice>>
    IsPositive --> Yes: > 0
    IsPositive --> No: <= 0
```

## Fork and Join (Concurrency)

Split into parallel regions with `fork`/`join`.

```mermaid
stateDiagram-v2
    [*] --> Start
    state fork1 <<fork>>
    Start --> fork1
    fork1 --> State1
    fork1 --> State2
    state join1 <<join>>
    State1 --> join1
    State2 --> join1
    join1 --> End
    End --> [*]
```

## Labeled Transitions with Conditions

Add guard conditions using `: condition` or `-->|label|`.

```mermaid
stateDiagram-v2
    Happy --> Sad: Tragedy
    Sad --> Happy: Comedy
    Happy --> Angry: Injustice
```

## Postconditions (Entry/Exit)

Use `entry` and `exit` actions inside state blocks.

```mermaid
stateDiagram-v2
    [*] --> ServerDown
    state ServerDown {
        entry: notify admin
        exit: log shutdown
        [*] --> CrashDetected
        CrashDetected --> Restarting
        Restarting --> [*]
    }
```
