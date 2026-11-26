# Sequence diagrams

Keyword: `sequenceDiagram`. Since v12.0.0 sequence diagrams default to the `redux-color` theme, `neo` look, and ELK layout.

Sources: `docs/syntax/sequenceDiagram.md`, `docs/syntax/all-examples.md` at mermaid@12.3.0.

## Participants

```mermaid
sequenceDiagram
    participant Alice
    participant Bob as Bob's alias
    participant John
    Alice->>John: Hello John, how are you?
```

- `participant <id> as <label>` sets a display alias.
- Typed participants: `actor`, `boundary`, `control`, `entity`, `database`, `collections`, `queue` declarations render typed shapes.
- Actor creation and destruction (v10.3.0+): `create participant B` / `create actor D as Donald` / `destroy Carl`. Only the recipient of a message can be created; sender or recipient can be destroyed. Destroying an actor ends its lifeline (`Alice-xCarl` draws the cross).

```mermaid
sequenceDiagram
    Alice->>Bob: Hello Bob, how are you ?
    create participant Carl
    Alice->>Carl: Hi Carl!
    destroy Carl
    Alice-xCarl: We are too many
    destroy Bob
```

- Grouping in boxes: `box <color?> <description?>` … `end`. The color value comes before the description; hex colors are not supported (`#` is comment syntax). `box transparent Aqua` forces a transparent color when the group name is a color keyword.

```mermaid
sequenceDiagram
    box Purple Alice & John
    participant A
    participant J
    end
    box Another Group
    participant B
    participant C
    end
    A->>J: Hello John, how are you?
```

## Messages

`[Actor][Arrow][Actor]:Message text`. Supported arrow types:

| Type | Meaning |
|---|---|
| `->` / `-->` | solid / dotted, no arrowhead |
| `->>` / `-->>` | solid / dotted arrowhead |
| `<<->>` / `<<-->>` | bidirectional arrowheads (v11.0.0+) |
| `-x` / `--x` | cross at the end |
| `-)` / `--)` | open arrow at the end (async) |

Half-arrows (v11.12.3+): solid/dotted variants like `-\|`, `-\|/`, `/\|-`, `\\-`, `-\\`, `-//`, `//-` give top/bottom half and stick arrowheads (increase dashes for dotted).

Central lifeline connections (v11.12.3+): messages can target a central point using `()` instead of an actor (see docs "Central Connections").

## Activations

```mermaid
sequenceDiagram
    Alice->>+Bob: Activate
    Bob-->>-Alice: Deactivate
```

`+`/`-` on the arrow head activates/deactivates the target; standalone `activate Bob` / `deactivate Bob` also work.

## Notes

```mermaid
sequenceDiagram
    Note right of Alice: text
    Note left of Bob: text
    Note over Alice,Bob: spans both
```

Line breaks: `<br>`/`<br/>`. Escape characters with entity codes (`#quot;` etc.).

## Fragments

```mermaid
sequenceDiagram
    Alice->>John: Hello John, how are you?
    loop HealthCheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts!
    John-->>Alice: Great!
```

Fragments: `alt <label>` … `else <label>` … `end`, `loop <label>` … `end`, `par <label>` … `and <label>` … `end`, `critical` … `end`, `break` … `end`, `opt` … `end`. Background highlighting: `rect rgb(...)` … `end`. `autonumber` numbers messages (start/increment values since v11.15.0).

## Styling and config

`classDef` + `class` style participants and links (docs "Styling" section lists the CSS classes used). Config params via frontmatter `config.sequence`: `mirrorActors`, `width`, `height`, `messageAlign`, `useMaxWidth`, `rightAngles`, `showSequenceNumbers`, `wrap`, plus actor/signal/note font keys.

## Verified examples

Basic (README example):

```mermaid
sequenceDiagram
Alice->>John: Hello John, how are you?
loop HealthCheck
    John->>John: Fight against hypochondria
end
Note right of John: Rational thoughts!
John-->>Alice: Great!
John->>Bob: How about you?
Bob-->>John: Jolly good!
```

Online payment flow (all-examples):

```mermaid
sequenceDiagram
    autonumber
    actor Customer
    participant Shop as Web Shop
    participant Pay as Payment Service
    participant Bank

    Customer->>Shop: Place order
    activate Shop
    Shop->>Pay: Create payment request
    activate Pay
    Pay->>Bank: Authorize card
    Bank-->>Pay: Authorization result
    alt Payment approved
        Pay-->>Shop: Payment confirmed
        Shop-->>Customer: Show receipt
    else Payment declined
        Pay-->>Shop: Payment failed
        Shop-->>Customer: Ask for another card
    end
    deactivate Pay
    deactivate Shop
```

## Gotchas

- The word `end` breaks the diagram — wrap it in parens, quotes, or brackets in participant names/message text.
- `box` blocks end with plain `end`, not `end box`.
- `wrap: true` (config) wraps long messages instead of truncating.
