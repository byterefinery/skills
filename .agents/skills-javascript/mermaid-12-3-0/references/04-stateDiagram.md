# State diagrams

Keyword: `stateDiagram-v2` (newer renderer) or `stateDiagram` (older renderer). PlantUML-like syntax. Since v12.0.0 state diagrams default to the `redux-color` theme, `neo` look, and ELK layout.

Sources: `docs/syntax/stateDiagram.md` at mermaid@12.3.0.

## Basics

```mermaid
---
title: Simple sample
---
stateDiagram-v2
    [*] --> Still
    Still --> [*]

    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
```

- `[*]` — start and end states.
- Transitions: `A --> B`, labeled `A --> B : event` or `A -- event --> B`.
- `direction LR` (or TD/BT/RL) sets the diagram direction.
- State labels: `NamedComposite: Another Composite` on a separate line.
- Spaces in state names need quotes.

## Composite states

`state <id> { … }` defines a composite state; nest to any depth. Transitions can exist between composite states, but not between internal states belonging to different composite states.

```mermaid
stateDiagram-v2
    [*] --> First
    state First {
        [*] --> second
        second --> [*]
    }

    [*] --> NamedComposite
    NamedComposite: Another Composite
    state NamedComposite {
        [*] --> namedSimple
        namedSimple --> [*]
        namedSimple: Another simple
    }
```

## Choice and forks

Choice uses the `<<choice>>` stereotype; forks use `<<fork>>`/`<<join>>`:

```mermaid
stateDiagram-v2
    state if_state <<choice>>
    [*] --> IsPositive
    IsPositive --> if_state
    if_state --> False: if n < 0
    if_state --> True : if n >= 0
```

```mermaid
stateDiagram-v2
    state fork_state <<fork>>
      [*] --> fork_state
      fork_state --> State2
      fork_state --> State3

      state join_state <<join>>
      State2 --> join_state
      State3 --> join_state
      join_state --> State4
      State4 --> [*]
```

## Notes

```mermaid
stateDiagram-v2
    State1: The state with a note
    note right of State1
        Important information! You can write
        notes.
    end note
    State1 --> State2
    note left of State2 : This is the note to the left.
```

## Concurrency

Inside a composite state, `--` on its own line separates concurrent regions:

```mermaid
stateDiagram-v2
    [*] --> Active

    state Active {
        [*] --> NumLockOff
        NumLockOff --> NumLockOn : EvNumLockPressed
        NumLockOn --> NumLockOff : EvNumLockPressed
        --
        [*] --> CapsLockOff
        CapsLockOff --> CapsLockOn : EvCapsLockPressed
        CapsLockOn --> CapsLockOff : EvCapsLockPressed
    }
```

## Styling

`classDef` + `class` apply CSS-like styles to states (see docs sections "Styling with classDefs" / "Apply classDef styles to states").

## Gotchas

- `stateDiagram-v2` is the richer renderer (composites, concurrency); the old `stateDiagram` keyword still works but with fewer features.
- You cannot define transitions between internal states belonging to different composite states.
- The word `end` is a block terminator — quote or capitalize it in state labels.
