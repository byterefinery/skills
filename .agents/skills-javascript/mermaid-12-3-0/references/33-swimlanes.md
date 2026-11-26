# Swimlanes diagrams

Keyword: `swimlane-beta` (beta, v11.16.0+). A process divided by responsibility: each lane is an actor, team, system, or phase; nodes show the work inside; arrows show order and handoffs. Since v12.0.0 swimlane diagrams default to the `redux-color` theme, `neo` look, and the `swimlane` layout.

Sources: `docs/syntax/swimlanes.md` at mermaid@12.3.0.

## Syntax

`swimlane-beta` optionally followed by a direction: `TB` (default), `TD`, `BT`, `LR`, `RL`.

- **Lanes**: top-level `subgraph` blocks render as swimlanes; end with `end`. Internal id + label: `subgraph sales [Sales team]`.
- A node belongs to one lane — if two lanes list the same node, it stays in the first; a lane emptied this way is removed (warnings logged; set `logLevel: 'warn'` to see).
- A subgraph nested inside a lane draws as a plain box, not a lane.
- **Nodes**: flowchart-style shape syntax (`id[Text]`, `id(Text)`, `id([Text])`, `id{Text}`, `id((Text))`); full catalog in the flowchart reference.
- **Edges**: flowchart-style — `A --> B`, `A --- B`, `A -->|Label| B`, `A -.-> B`, `A ==> B`, same or across lanes.

```mermaid
swimlane-beta LR
  subgraph Customer
    Browse[Browse catalogue]
    Pay[Pay]
  end
  subgraph Warehouse
    Pick[Pick items]
    Ship[Ship order]
  end
  subgraph Finance
    Invoice[Raise invoice]
  end
  Browse --> Pay
  Pay --> Pick
  Pick --> Ship
  Pay --> Invoice
```

## Accessibility

`accTitle:` and `accDescr:` lines provide accessible title/description.

## Good practices (from the docs)

- Make each lane mean one kind of ownership.
- Label cross-lane handoffs.
- Keep long processes readable (stable ids, decisions where they are made).
- "When to use another diagram" — the docs list when a plain flowchart or agentflow fits better.
