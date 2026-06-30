---
name: antv-infographic-0-2-19
description: >
  Render declarative SVG infographics with @antv/infographic 0.2.19. Use when generating
  professional data visualizations — lists, sequences, hierarchies, comparisons, charts,
  relation graphs — as self-contained HTML or raw SVG. Supports a concise YAML-like syntax,
  streaming AI rendering, built-in editor, JSX custom components, SSR, and theme/stylize system.
  File extensions: none (library is imported). Trigger on: infographic, data visualization,
  SVG chart, flowchart, timeline, mindmap, SWOT, funnel, pie chart, bar chart.
metadata:
  tags:
    - javascript
    - visualization
    - svg
    - chart
---

# antv-infographic 0.2.19

## Overview

AntV Infographic is a declarative SVG infographic engine. It composes infographics from a *template* (pre-built layout combining a structure + item components), a *design* (custom structure/item/title overrides), and *data*. The library renders to SVG by default, supports an optional built-in editor, SSR via `renderToString`, and a JSX-based system for custom components.

The library accepts two input forms:

1. **Infographic syntax** — a concise, YAML-like text format parsed at runtime. Fault-tolerant enough for streaming AI output.
2. **JS object options** — full `InfographicOptions` passed directly.

### Core Concepts

- **Template** — a named preset (e.g., `list-row-simple-horizontal-arrow`) combining a structure layout and item component(s). ~130 built-in templates.
- **Structure** — the layout engine (e.g., `list-row`, `sequence-steps`, `hierarchy-tree`, `compare-quadrant`, `relation-network`). ~35 built-in structures.
- **Item** — how each data point is rendered (e.g., `badge-card`, `simple`, `circular-progress`, `plain-text`). ~28 built-in items.
- **Theme** — color/font/stylization preset (`default`, `light`, `dark`, `hand-drawn`). Deep customization via `themeConfig`.
- **Data** — the content. Organized by type: `lists`, `sequences`, `root` (hierarchy), `compares`, `nodes`/`relations` (graph), `values` (statistics).
- **Resources** — icons and illustrations loaded via built-in protocols (Data URI, remote URL, search) or custom loaders.

### Six Infographic Types

| Type | Data Key | Example Templates |
|---|---|---|
| **List** | `lists` | `list-grid-compact-card`, `list-row-simple-horizontal-arrow`, `list-pyramid-badge-card` |
| **Sequence** | `sequences` | `sequence-steps-simple`, `sequence-timeline-done-list`, `sequence-snake-steps-compact-card` |
| **Hierarchy** | `root` | `hierarchy-mindmap-compact-card`, `hierarchy-tree-simple`, `hierarchy-structure` |
| **Compare** | `compares` | `compare-swot`, `compare-binary-horizontal-simple-vs`, `quadrant-quarter-simple-card` |
| **Relation** | `nodes` + `relations` | `relation-dagre-flow-tb-simple-circle-node`, `relation-network-icon-badge` |
| **Statistics** | `values` | `chart-column-simple`, `chart-pie-plain-text`, `word-cloud-simple` |

### Installation

```bash
npm install @antv/infographic@0.2.19
```

### CLI Scripts — Validate and Render

The skill ships with two scripts in `scripts/`:

- **`infographic.sh`** — thin Bash wrapper that delegates to `_infographic.js` via `bun`
- **`_infographic.js`** — Bun script importing `@antv/infographic` (parser) and `@antv/infographic/ssr` (renderer)

Requires [Bun](https://bun.sh) runtime. The `bun` installer resolves `@antv/infographic` at runtime.

#### Validation

Uses the **official `parseSyntax()`** from `@antv/infographic` — errors and warnings are exactly what the library produces, not a custom approximation.

```bash
# Validate a standalone .ifgc file
infographic.sh validate chart.ifgc

# Validate infographic blocks inside a markdown file
infographic.sh validate notes.md

# Recursively validate all matching files in a directory
infographic.sh validate ./docs/

# Validate from stdin
cat chart.ifgc | infographic.sh validate -
```

**Input modes:**

| Input | Behavior |
|---|---|
| `.ifgc` | Entire file is one infographic spec |
| `.md` / `.mdx` / `.markdown` | Extracts ````infographic` fenced blocks; a single file can contain many blocks, each validated independently |
| `-` (stdin) | Reads raw infographic syntax from stdin |
| directory | Recursively finds `.md`, `.mdx`, `.markdown`, `.ifgc` files |

**Options:**

| Flag | Effect |
|---|---|
| `-q`, `--quiet` | Only output errors (suppress valid-file markers) |
| `-w`, `--warnings` | Also display parser warnings (default: errors only) |
| `--json` | Machine-readable JSON output |

**Exit codes:** 0 = all valid (or no blocks found), 1 = syntax errors, 2 = usage error.

#### Rendering

Uses **`renderToString()`** from `@antv/infographic/ssr` — server-side rendering via `linkedom` (virtual DOM, no browser needed). Each block is **validated first**; invalid blocks are skipped with error output.

```bash
# Render a standalone .ifgc file to SVG (output: chart.svg)
infographic.sh render -i chart.ifgc

# Render to a specific path
infographic.sh render -i chart.ifgc -o output.svg

# Render all infographic blocks from a markdown file into a directory
infographic.sh render -i notes.md -d ./output/

# Render only block 2 from a markdown file
infographic.sh render -i notes.md -b 2 -o block2.svg

# Override dimensions
infographic.sh render -i chart.ifgc -w 800 -H 600
```

**Options:**

| Flag | Effect |
|---|---|
| `-i`, `--input` | Input file (required) — `.ifgc` or `.md` with ````infographic` fenced blocks |
| `-o`, `--output` | Output file path (`.svg` or `.png`). Default: same name as input with `.svg` |
| `-d`, `--dir` | Output directory (creates if missing). Used with multi-block inputs |
| `-b`, `--block` | Render only block N from markdown files (1-indexed) |
| `-w`, `--width` | SVG width in px (default: auto from template) |
| `-H`, `--height` | SVG height in px (default: auto from template) |

**Output naming:**

| Scenario | Output path |
|---|---|
| `-o output.svg` with single block | Exact path given |
| `-o output.svg` with multiple blocks | `basename-blockN.svg` in same directory |
| `-d ./output/` | `basename.svg` (or `basename-blockN.svg`) inside the directory |
| No output flags | `basename.svg` next to input file |

**Exit codes:** 0 = all rendered, 1 = one or more failures, 2 = usage error.

## Usage

### List — Checklist, Features, Rankings

```infographic
infographic list-grid-compact-card
data
  title Project Milestones
  lists
    - label Design
      desc UI/UX completed
      value 100
    - label Development
      desc In progress
      value 65
    - label Testing
      desc Pending
      value 20
theme
  palette antv
```

### Sequence — Steps, Timeline, Workflow

```infographic
infographic sequence-steps-simple
data
  title Deployment Pipeline
  sequences
    - label Build
      desc Compile and bundle
    - label Test
      desc Run CI suite
    - label Deploy
      desc Push to production
theme
  palette antv
```

### Hierarchy — Org Chart, Mindmap, Taxonomy

```infographic
infographic hierarchy-structure
data
  title Tech Stack
  root
    label Frontend
    children
      - label React
      - label Vue
    label Backend
    children
      - label Node.js
      - label Go
theme
  palette antv
```

### Compare — SWOT, Pros/Cons, Quadrant

```infographic
infographic compare-swot
data
  title Plan Comparison
  compares
    - label Plan A
      value 75
      children
        - label Faster delivery
        - label Lower cost
    - label Plan B
      value 90
      children
        - label Higher quality
        - label Better scalability
theme
  palette antv
```

### Relation — Flowchart, Network, System Diagram

```infographic
infographic relation-dagre-flow-tb-simple-circle-node
data
  title Request Flow
  nodes
    - id client
      label Client
    - id api
      label API Server
    - id db
      label Database
  relations
    client -> api
    api -> db
theme
  palette antv
```

### Statistics — Column Chart, Pie, Word Cloud

```infographic
infographic chart-column-simple
data
  title Monthly Revenue
  values
    - label Jan
      value 120
    - label Feb
      value 180
    - label Mar
      value 250
theme
  palette antv
```

See [07-usage](references/07-usage.md) for browser API, SSR, streaming, export, events, and editor.

## Gotchas

- **Always wrap infographic syntax in ` ```infographic ` code blocks in markdown** — bare infographic syntax outside fenced code blocks is not portable and won't be detected by the validator or renderer. Use the language hint `infographic` on the opening fence.
- **Data key matters by template type** — list templates expect `lists`, sequence templates expect `sequences`, hierarchy templates expect `root`, comparison templates expect `compares`, relation templates expect `nodes` + `relations`, chart/statistics templates expect `values`. Using the wrong key results in empty rendering.
- **`value` must be a number for chart items** — when a template uses `usePaletteColor: true` or `showIcon: false` (like `chart-column-simple`), items need a numeric `value` field. Strings won't produce meaningful bars.
- **Syntax indentation is significant** — the parser uses indent-based nesting (spaces or tabs). A `- label` under `lists` must be indented relative to `lists`. Mixed indentation within one level causes parsing errors.
- **Template name vs bare first line** — writing `list-row-simple-horizontal-arrow` on the first line (without `infographic` prefix) works but emits a warning. Use `infographic <template>` or `template <name>` for clarity.
- **SSR needs Node.js with `linkedom`** — `renderToString` uses `linkedom` internally for a virtual DOM. It works in Node without a browser. The 10-second timeout is fixed.
- **`editable: true` requires a browser** — the editor (drag, select, edit bar, zoom) only works in a real DOM. SSR and headless environments must omit `editable`.
- **Font loading is async** — built-in fonts (Alibaba PuHuiTi, Source Han Sans, etc.) load from CDN. The `loaded` event fires after fonts + images resolve. Use it before export.
- **Relations syntax uses ASCII arrows** — under `data relations`, lines like `A --> B` or `A <-[label]-> B` are parsed as graph edges. Node labels go in `[brackets]` or `(parens)`. This is a special sub-syntax, not generic key-value.
- **Custom JSX components need `jsx-runtime`** — when writing `.tsx` custom items/structures, import from `'@antv/infographic/jsx-runtime'` and configure tsconfig JSX to `react-jsx` with the custom import path.
- **Palette as single color auto-generates series** — `palette: '#1677ff'` in themeConfig creates a gradient series from that seed. For explicit colors, pass an array: `palette: ['#1677ff', '#00C9C9', '#F0884D']`.
- **`theme: 'hand-drawn'` requires the `851tegakizatsu` font** — it sets `font-family` to that font and enables `rough` stylization. If the font fails to load, it falls back to system fonts but keeps the rough look.
- **`items` vs `items[]` in design** — `design.item` applies one item type to all data points. `design.items` is an array for multi-level hierarchies (different item per depth level).
- **Dotted paths can't traverse arrays** — `theme.base.text.fill: red` works, but `data.items.0.label: X` fails. Dotted paths are for object nesting only.
- **`ref:remote` resources need CORS** — remote URLs loaded via the built-in `ref:remote` protocol require the server to set proper CORS headers.
- **Resource loader is singleton** — `registerResourceLoader` replaces the previous loader. Handle all resource types within one registration.
- **`width`/`height` in constructor, not syntax** — container-specific options (`width`, `height`, `padding`, `editable`) go in `new Infographic({...})`. Inside syntax, only define `template`, `design`, `data`, and `theme`.
- **Palette colors cycle** — when data items exceed palette length, colors repeat cyclically (4th item uses 1st color, etc.).

## References

- [01-syntax](references/01-syntax.md) — Complete syntax reference with full examples for all 6 infographic types (list, sequence, hierarchy, compare, relation, statistics)
- [02-templates](references/02-templates.md) — Built-in templates (~130), structures (~35), items (~28), decorations
- [03-jsx-custom-components](references/03-jsx-custom-components.md) — JSX system: primitive nodes, built-in components, layout system, custom items/structures
- [04-themes-stylize](references/04-themes-stylize.md) — Theme system, palettes, gradients, patterns, rough stylization, fonts
- [05-resources](references/05-resources.md) — Resource loading: built-in protocols, custom loaders, helper functions, best practices
- [06-official-examples](references/06-official-examples.md) — All 41 examples from the official @antv/infographic 0.2.19 repo docs, validated and rendered
- [07-usage](references/07-usage.md) — Browser API, SSR, streaming rendering, export, events, custom resource loader, built-in editor
