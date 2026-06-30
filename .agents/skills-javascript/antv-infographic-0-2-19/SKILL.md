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

### CLI — Validate and Render

```bash
# Validate syntax (standalone .infographic files or fenced blocks in .md)
infographic.sh validate file.infographic
infographic.sh validate notes.md
infographic.sh validate ./directory/

# Render to SVG
infographic.sh render -i chart.infographic -o output.svg
infographic.sh render -i notes.md -d ./output/

# Validate from stdin
cat chart.infographic | infographic.sh validate -
```

## Usage

### Browser — Syntax Input (Recommended)

```html
<div id="container"></div>
<script type="module">
import { Infographic } from '@antv/infographic';

const chart = new Infographic({ container: '#container' });

chart.render(`
infographic list-row-simple-horizontal-arrow
data
  title Project Progress
  lists
    - label Step 1
      desc Start
    - label Step 2
      desc In Progress
    - label Step 3
      desc Complete
`);
</script>
```

### Browser — JS Object Input

```ts
import { Infographic } from '@antv/infographic';

const chart = new Infographic({
  container: '#container',
  width: '100%',
  height: 600,
  editable: true,
});

chart.render({
  template: 'list-row-simple-horizontal-arrow',
  data: {
    lists: [
      { label: 'Step 1', desc: 'Start' },
      { label: 'Step 2', desc: 'In Progress' },
      { label: 'Step 3', desc: 'Complete' },
    ],
  },
});
```

### Streaming Rendering

The syntax parser is fault-tolerant — render partial output as AI streams tokens:

```ts
let buffer = '';
for (const chunk of aiChunks) {
  buffer += chunk;
  chart.render(buffer);
}
```

### SSR — Server-Side Render to SVG String

```ts
import { renderToString } from '@antv/infographic/ssr';

const svgString = await renderToString(`
infographic chart-column-simple
data
  title Sales
  values
    - label Q1
      value 120
    - label Q2
      value 200
    - label Q3
      value 180
    - label Q4
      value 250
`);
```

### Export

```ts
// After render() and in browser
const svgDataUrl = await chart.toDataURL({ type: 'svg' });
const pngDataUrl = await chart.toDataURL({ type: 'png', dpr: 2 });
```

### Events

```ts
chart.on('rendered', ({ node, options }) => {
  console.log('SVG rendered', node);
});

chart.on('loaded', ({ node, options }) => {
  console.log('All resources loaded', node);
});

chart.on('error', (errors) => {
  console.error('Render errors', errors);
});
```

### Update / Destroy

```ts
// Merge new options into existing
chart.update({ data: { lists: newItems } });

// Full replacement
chart.render(newOptions);

// Cleanup
chart.destroy();
```

### Custom Resource Loader

Register a loader to fetch icons/illustrations from your own service:

```ts
import { registerResourceLoader, loadSVGResource } from '@antv/infographic';

registerResourceLoader(async (config) => {
  const { data, scene = 'icon' } = config;
  const response = await fetch(`https://api.iconify.design/${data}.svg`);
  const svgText = await response.text();
  return loadSVGResource(svgText);
});
```

### Editor (Built-in)

Set `editable: true` to enable selection, dragging, text editing, and zoom. Default plugins: `EditBar`, `ResizeElement`, `ResetViewBox`. Default interactions: `DragCanvas`, `DblClickEditText`, `BrushSelect`, `ClickSelect`, `DragElement`, `HotkeyHistory`, `ZoomWheel`, `SelectHighlight`.

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
