---
name: mermaid-11-15-0
description: >
  Mermaid diagram syntax reference and validation. Use when writing, debugging,
  or converting Mermaid diagrams. Every diagram must pass mermaid.sh validate
  before output. Supports: flowchart, sequenceDiagram, stateDiagram, classDiagram,
  gantt, erDiagram, pie, gitgraph, journey, mindmap, timeline, xychart, radar-beta,
  quadrantChart, sankey, block, architecture-beta, c4, packet, treemap-beta, venn-beta,
  wardley-beta, ishikawa-beta, kanban, requirementDiagram.
metadata:
  tags:
    - diagrams
    - visualization
    - documentation
---

# mermaid 11.15.0

## Overview

Mermaid generates diagrams from plain-text descriptions. Write diagram syntax inside a markdown code block fenced with ` ```mermaid `.

All supported diagram types: flowcharts/graphs, sequence diagrams, state diagrams (v2), class diagrams, Gantt charts, entity-relationship diagrams, pie charts, git commit graphs, user journey diagrams, mindmaps, timelines, XY charts (bar/line), radar charts, quadrant charts, Sankey flow diagrams, block diagrams, cloud architecture diagrams, C4 model diagrams (context/container/component/dynamic/deployment), network packet diagrams, treemaps, Venn diagrams, Wardley strategy maps, Ishikawa fishbone diagrams, Kanban boards, and SysML requirement diagrams.

This skill provides syntax reference for every diagram type and a validation pipeline using the official Mermaid parser.

## Usage

### Validate a diagram

Validate mermaid code from stdin:

```bash
echo 'flowchart LR
    A-->B' | mermaid.sh validate -
```

Validate a markdown file (checks all ` ```mermaid ` blocks):

```bash
mermaid.sh validate ./docs/diagram.md
```

Validate a directory recursively:

```bash
mermaid.sh validate ./docs/ --quiet
```

JSON output:

```bash
mermaid.sh validate --json ./diagram.md
```

### Convert to SVG/PNG

Use `mermaid.sh render` to convert `.mmd` or `.md` files to SVG or PNG:

```bash
# Single file to SVG (default output format)
mermaid.sh render -i diagram.mmd

# Explicit output path
mermaid.sh render -i diagram.mmd -o diagram.svg
mermaid.sh render -i diagram.mmd -o diagram.png

# With theme
mermaid.sh render -i diagram.mmd -t dark -o diagram.svg

# From a markdown file (extracts mermaid blocks)
mermaid.sh render -i notes.md -o output/
```

The script reads `.mmd` files (raw mermaid) or `.md` files (extracts fenced mermaid blocks). Output format is inferred from the `-o` extension (default: `.svg`). Run `mermaid.sh render --help` for all options.

### Diagram types at a glance

| Keyword | Diagram Type |
|---|---|
| `flowchart` / `graph` | Flowcharts and graphs |
| `sequenceDiagram` | Sequence diagrams |
| `stateDiagram-v2` / `stateDiagram` | State diagrams |
| `classDiagram` | Class (UML) diagrams |
| `gantt` | Gantt charts |
| `erDiagram` | Entity-relationship diagrams |
| `pie` | Pie charts |
| `gitGraph` | Git commit graphs |
| `journey` | User journey diagrams |
| `mindmap` | Mind maps |
| `timeline` | Timeline diagrams |
| `xychart` | XY charts (bar/line) |
| `radar-beta` | Radar/spider charts |
| `quadrantChart` | Quadrant charts |
| `sankey` | Sankey flow diagrams |
| `block` | Block diagrams |
| `architecture-beta` | Cloud architecture |
| `C4Context` / `C4Container` / etc. | C4 model diagrams |
| `packet` | Network packet diagrams |
| `treemap-beta` | Treemap diagrams |
| `venn-beta` | Venn diagrams |
| `wardley-beta` | Wardley maps |
| `ishikawa-beta` | Fishbone/Ishikawa |
| `kanban` | Kanban boards |
| `requirementDiagram` | Requirements (SysML) |

## Validation Workflow

Every Mermaid diagram must pass validation before being shown to the user or written to a file. Follow this loop without skipping steps:

1. **Write** the diagram inside a ` ```mermaid ` code block in a `.md` or `.mmd` file.
2. **Validate** by running:
   - `mermaid.sh validate -` (pipe diagram code to stdin for quick checks)
   - `mermaid.sh validate <file>` (for `.md` or `.mmd` files)
3. **Fix** every parser error reported. Read the error message carefully — it identifies the syntax issue and line.
4. **Re-validate** after every fix. Repeat steps 2–4 until validation exits with code 0 (all diagrams valid).
5. **Output** only after the last validation passes clean.

**Rules:**
- **Never output or show a diagram that hasn't passed validation.** If validation fails, fix and retry silently — do not present broken diagrams to the user.
- **Only valid ` ```mermaid ` code blocks in `.md` or `.mmd` files are allowed.** No raw mermaid text, no ` ```mermaid-example ` fences, no other file extensions.
- **Resolve every error.** Do not stop after fixing the first error — the parser may report one error at a time. Keep iterating until the exit code is 0.
- **For stdin validation**, pipe just the diagram body (no fence markers):
  ```bash
  echo 'flowchart LR
      A-->B' | mermaid.sh validate -
  ```

## Gotchas

- **Validation is mandatory, not optional** — run `mermaid.sh validate -` (stdin) or `mermaid.sh validate <file>` after every diagram you write. Fix all reported errors iteratively until exit code is 0. Never present an unvalidated or invalid diagram to the user.
- **Parser reports one error at a time** — fixing one syntax error may reveal the next. Always re-validate after each fix; don't assume one pass is enough. A diagram with three typos will produce three separate validation rounds.
- **Only `.md` and `.mmd` files** — write mermaid diagrams exclusively to `.md` (fenced blocks) or `.mmd` (raw diagram) files. Do not embed mermaid in `.txt`, `.html`, or other formats.
- **The word `end` breaks flowcharts** — if a node label contains lowercase "end", capitalize it ("End") or wrap in quotes. Same applies to sequence diagrams: use parentheses, brackets, or quotes around the word.
- **Leading `o` or `x` in flowchart nodes** — `A---oB` creates a circle edge, not a node named "oB". Add a space or capitalize: `A--- Ops`.
- **Every example must start with ` ```mermaid`** — the validator extracts blocks matching this fence. Do not use ` ```mermaid-example` or other variants in final output.
- **Beta diagrams use `-beta` suffix** — `radar-beta`, `architecture-beta`, `treemap-beta`, `venn-beta`, `wardley-beta`, `ishikawa-beta`. The keyword must include the suffix.
- **`stateDiagram-v2` vs `stateDiagram`** — prefer `stateDiagram-v2` (newer renderer with composite states, concurrency). The older `stateDiagram` still works but lacks features.
- **YAML frontmatter config** — diagram-level configuration goes between `---` fences before the diagram keyword. Use `config:` for per-diagram settings and `title:` for display titles.
- **Use `--json` for scripted iteration** — `mermaid.sh validate --json -` outputs structured JSON, making it easier to parse errors when automating fix loops.

## References

Each reference file covers one diagram type with syntax rules and validated examples:

- [01-flowchart.md](references/01-flowchart.md) — Flowcharts, graphs, node shapes, edges, subgraphs, styling
- [02-sequenceDiagram.md](references/02-sequenceDiagram.md) — Participants, messages, activations, loops, alt/opt
- [03-stateDiagram.md](references/03-stateDiagram.md) — States, transitions, composite states, forks, concurrency
- [04-classDiagram.md](references/04-classDiagram.md) — Classes, inheritance, composition, namespaces, generics
- [05-gantt.md](references/05-gantt.md) — Tasks, sections, milestones, dependencies, date formats
- [06-erDiagram.md](references/06-erDiagram.md) — Entities, relationships, cardinality, attributes, keys
- [07-pie.md](references/07-pie.md) — Pie charts with slices and data labels
- [08-gitGraph.md](references/08-gitGraph.md) — Commits, branches, merges, cherry-picks, orientations
- [09-userJourney.md](references/09-userJourney.md) — User journeys with sections, tasks, scores
- [10-mindmap.md](references/10-mindmap.md) — Hierarchical mindmaps, shapes, icons, markdown strings
- [11-timeline.md](references/11-timeline.md) — Timelines with sections, events, directions
- [12-xyChart.md](references/12-xyChart.md) — Bar and line charts on x/y axes
- [13-radar.md](references/13-radar.md) — Radar/spider charts with multiple curves
- [14-quadrantChart.md](references/14-quadrantChart.md) — Four-quadrant scatter plots
- [15-sankey.md](references/15-sankey.md) — Flow/sankey diagrams showing value transfers
- [16-block.md](references/16-block.md) — Block diagrams with full layout control
- [17-architecture.md](references/17-architecture.md) — Cloud architecture with groups and services
- [18-c4.md](references/18-c4.md) — C4 model (context, container, component)
- [19-packet.md](references/19-packet.md) — Network packet structure diagrams
- [20-treemap.md](references/20-treemap.md) — Hierarchical treemap visualizations
- [21-venn.md](references/21-venn.md) — Set relationships with overlapping circles
- [22-wardley.md](references/22-wardley.md) — Wardley strategy maps
- [23-ishikawa.md](references/23-ishikawa.md) — Cause-and-effect fishbone diagrams
- [24-kanban.md](references/24-kanban.md) — Kanban workflow boards
- [25-requirementDiagram.md](references/25-requirementDiagram.md) — SysML requirement diagrams
