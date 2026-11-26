# Agentflow

Keyword: `agentflow-beta` (beta, v12.0.0+). Describes agentic workflows: agents, flows, tasks, tools, and how control/data move. Since v12.0.0 agentflow diagrams default to the `redux-color` theme, `neo` look, and ELK layout.

Sources: `docs/syntax/agentflow.md` at mermaid@12.3.0.

## Declaration

`agentflow-beta` followed optionally by a direction — `TB`, `TD`, `BT`, `LR`, `RL`.

## Nodes and shapes

Nodes: an id, optionally a label in brackets. Shape via `shape` key in an `@{ … }` block. Domain aliases:

| Alias | Meaning | Underlying shape |
|---|---|---|
| `task` | unit of work an agent performs | `roundedRect` |
| `tool` | callable capability (function/API/subroutine) | `subroutine` |
| `input` | data entering the workflow | `lean-right` |
| `decision` | branch point | `diamond` |
| `refdoc` | reference material consulted | `lin-doc` |
| `action` | side-effecting step | `hexagon` |

Any canonical Mermaid shape name works too.

## Edges

| Operator | Semantic |
|---|---|
| `-->` | sequence — control/data flows source → target |
| `-.-` | reference — source consults target; no control passes |
| `--x` | failure — failure path out of the source |

Labels go in the middle of the arrow (`check -- yes --> ship`). Chained edges work.

## Containers

- `flow <id>["Label"]` … `end` groups nodes; containers nest.
- `global` … `end` keeps nodes at top level regardless of references (no id/label/metadata; renders nothing).
- `processing@{ view: "collapsed" }` folds a container to a summary node (boundary edges terminate at it).
- Per-container ELK algorithm: `tools@{ algorithm: "elk.rectpacking" }`.

## Metadata

`@{ … }` blocks on nodes, edges, or containers are YAML. Mermaid-acted keys: `shape`, `label`/`labelType` (nodes), `view` (containers), `algorithm` (containers), `curve`/`animate`/`animation` (edges). Convention keys carried through untouched: `description`, `instruction` (agents/flows), `model`, `params` (e.g. `"city :: String"`), `returns`, `value`/`example` (inputs), `connectorRef` (tools/actions). Unknown keys are preserved, never rejected; `__proto__`/`constructor`/`prototype` are stripped.

## Connectors

`connector <id>["Label"]` declares an external system; tools bind via `connectorRef` (bare id, dotted `connector.capability`, or URL):

```mermaid
agentflow-beta LR
  connector github["GitHub API"]
  github@{ protocol: "http", endpoint: "https://api.github.com" }

  title["Issue title"]@{ shape: input }
  create["create_issue"]@{ shape: tool, connectorRef: "github.create_issue" }

  title --> create
```

## Configuration

`agentflow:` config namespace: `titleTopMargin` (25), `diagramPadding` (8), `nodeSpacing` (50), `rankSpacing` (50), `useMaxWidth` (true). Theme variable `flowContainerStroke` themes containers.

## Verified examples

Basic (docs):

```mermaid
agentflow-beta TB
  flow reviewer["Review Agent"]
    changes["Gather changes"]@{ shape: input }
    analyse["Analyse diff"]@{ shape: task }
    lint["run_linter"]@{ shape: tool }
    ok["Clean?"]@{ shape: decision }

    changes --> analyse --> lint --> ok
  end
```

Coffee team worked example (docs) — flows `researcher`/`designer` inside `coffee_team`, with tools bound to an `llm` connector and a `refdoc` consulted via `-.-`.

## For tool builders

The diagram DB exposes `getSemanticModel()` (presentation-only keys stripped) and `getDiagnostics()` (structured warnings — unresolved references, misapplied metadata keys, containment violations; warnings never block a render).

## Gotchas

- 12.3.0 fix: `a[/…/]` short form renders as an input (previously fell back to a task with a SHAPE_UNSUPPORTED warning).
- `global` may appear anywhere, including nested inside a flow, as an escape hatch.
