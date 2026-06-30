# Templates, Structures & Items Reference

## Built-in Structures (~35)

Structures define the layout. Each structure type accepts props for fine-tuning.

### List Structures

| Type | Description | Key Props |
|---|---|---|
| `list-row` | Horizontal row layout | `gap`, `zigzag` |
| `list-column` | Vertical column layout | `width`, `gap`, `zigzag` |
| `list-grid` | Grid/matrix layout | `columns`, `gap`, `zigzag` |
| `list-pyramid` | Pyramid shape (wide bottom, narrow top) | `gap`, `levelGap` |
| `list-sector` | Circular sector/fan layout | `outerRadius`, `innerRadius`, `startAngle`, `endAngle`, `gapAngle` |
| `list-waterfall` | Waterfall cascade layout | `columns`, `gap`, `stepOffset` |

### Sequence Structures

| Type | Description | Key Props |
|---|---|---|
| `sequence-steps` | Horizontal numbered steps | `gap` |
| `sequence-timeline` | Vertical timeline | `gap`, `lineOffset` |
| `sequence-snake-steps` | Snake/winding path steps | `gap`, `itemsPerRow`, `rowGap` |
| `sequence-color-snake-steps` | Snake with color-coded steps | `gap`, `itemsPerRow`, `rowGap`, `columnGap`, `circleStrokeWidth` |
| `sequence-ascending-steps` | Ascending step layout | `hGap`, `vGap` |
| `sequence-ascending-stairs-3d` | 3D ascending stairs | `cubeWidth` |
| `sequence-zigzag-pucks-3d` | 3D puck zigzag | `gap` |
| `sequence-horizontal-zigzag` | Horizontal zigzag | `gap`, `cardPadding` |
| `sequence-zigzag-steps` | Zigzag numbered steps | `dx`, `dy`, `iconSize` |
| `sequence-circular` | Circular/radial sequence | `outerRadius`, `innerRadius`, `itemDistance`, `gapAngle`, `iconRadius`, `iconBgRadius`, `iconSize` |
| `sequence-circle-arrows` | Circle with directional arrows | `radius`, `arrowSize`, `strokeWidth` |
| `sequence-roadmap-vertical` | Vertical roadmap | `spacing`, `flipped` |
| `sequence-pyramid` | Pyramid sequence | `gap`, `width`, `pyramidWidth`, `itemHeight` |
| `sequence-funnel` | Funnel (wide→narrow) | — |
| `sequence-filter-mesh` | Filter mesh layout | `gap` |
| `sequence-mountain` | Mountain peak layout | `gap`, `minHeight`, `maxHeight`, `minWidth`, `maxWidth` |
| `sequence-cylinders-3d` | 3D cylinder layout | `cylinderRx`, `cylinderRy`, `baseHeight`, `heightIncrement`, `horizontalSpacing`, `depthSpacing`, `itemVerticalAlign`, `itemVerticalOffset` |
| `sequence-interaction` | Interaction diagram | — |
| `sequence-stairs-front` | Front-facing stairs | — |

### Comparison Structures

| Type | Description | Key Props |
|---|---|---|
| `compare-binary-horizontal` | Two-column comparison (pros/cons, vs) | `gap`, `groupGap`, `opposite`, `flipped`, `dividerType` |
| `compare-hierarchy-left-right` | Left-right hierarchy comparison | `gap`, `groupGap`, `surround`, `decoration`, `flipRoot`, `flipLeaf` |
| `compare-hierarchy-row` | Row-based hierarchy comparison | `gap`, `itemGap`, `columnWidth`, `itemPadding`, `showColumnBackground`, `columnBackgroundAlpha` |
| `compare-quadrant` | Four-quadrant matrix | `quadrantWidth`, `quadrantHeight`, `showAxis`, `dashedAxis` |

### Hierarchy Structures

| Type | Description | Key Props |
|---|---|---|
| `hierarchy-tree` | Tree layout | `levelGap`, `nodeGap`, `edgeType`, `edgeColorMode`, `edgeWidth`, `edgeStyle`, `edgeDashPattern`, `edgeCornerRadius`, `edgeOffset`, `edgeOrigin`, `edgeOriginPadding`, `edgeMarker`, `markerSize`, `colorMode` |
| `hierarchy-mindmap` | Mind map | — |
| `hierarchy-structure` | Org chart / structure diagram | — |

### Chart Structures

| Type | Description | Key Props |
|---|---|---|
| `chart-column` | Vertical bar chart | `columnGap`, `columnWidth`, `padding`, `showValue`, `valueFormatter` |
| `chart-bar` | Horizontal bar chart | — |
| `chart-line` | Line chart | — |
| `chart-pie` | Pie/donut chart | — |
| `chart-wordcloud` | Word cloud | — |

### Relation Structures

| Type | Description | Key Props |
|---|---|---|
| `relation-circle` | Circular node layout | `radius`, `startMode` |
| `relation-network` | Force-directed network | `spacing`, `showConnections` |
| `relation-dagre-flow` | DAG/flowchart (topological) | — |

## Built-in Items (~28)

Items define how each data point is visually rendered.

| Type | Description | Key Props |
|---|---|---|
| `simple` | Minimal text + optional icon | `width`, `height`, `gap`, `showIcon`, `iconSize`, `iconType`, `usePaletteColor` |
| `simple-illus` | Text with illustration | `width`, `illusSize`, `gap`, `usePaletteColor` |
| `simple-horizontal-arrow` | Text with horizontal arrow connector | `width`, `flipped` |
| `simple-vertical-arrow` | Text with vertical arrow connector | `height`, `flipped` |
| `simple-circle-node` | Circle node with text | — |
| `badge-card` | Card with colored badge | `width` (200), `height` (80), `iconSize` (24), `badgeSize` (32), `gap` (8) |
| `compact-card` | Compact card layout | `width` (200), `height` (60), `iconSize` (20), `gap` (8) |
| `candy-card-lite` | Light candy-style card | `width` (280), `height` (140) |
| `progress-card` | Card with progress bar | `width` (280), `height` (120), `iconSize` (32), `gap` (12), `progressHeight` (8), `borderRadius` (12) |
| `ribbon-card` | Card with ribbon accent | `width` (240), `height` (140), `iconSize` (28), `gap` (12), `ribbonHeight` (32) |
| `capsule-item` | Capsule/pill-shaped item | `width` (300), `height` (80), `gap` (12), `iconPadding` |
| `circle-node` | Circle node | `width`, `height` (240) |
| `circular-progress` | Circular progress ring | `size` (120), `strokeWidth` (12), `gap` (8) |
| `done-list` | Checklist/done list item | `width` (300), `height` (30), `iconSize` (30), `gap` (5) |
| `horizontal-icon-arrow` | Icon + arrow, horizontal | `width` (140) |
| `horizontal-icon-line` | Icon + line, horizontal | `width` (160) |
| `vertical-icon-arrow` | Icon + arrow, vertical | `height` (140), `flipped` |
| `icon-badge` | Icon with badge | `size` (80), `iconSize` (28), `badgeSize` (24), `gap` (8) |
| `indexed-card` | Card with index number | `width` (200), `borderRadius` (12), `padding` (16), `separatorHeight` (2), `indexFontSize` (20), `labelFontSize` (16), `gap` (8) |
| `l-corner-card` | L-corner accent card | `width` (140), `iconSize` (24) |
| `letter-card` | Card with letter initial | `width` (280), `height` (160), `showStripe`, `showGradient`, `showBottomShade` |
| `lined-text` | Text with underline decoration | — |
| `pill-badge` | Pill-shaped badge | `width` (300), `pillWidth` (120), `pillHeight` (36), `gap` (16) |
| `plain-text` | Plain text only | `width` (120), `formatter`, `usePaletteColor` |
| `quarter-circular` | Quarter-circle layout | `width` (280), `height` (120), `iconSize` (30), `circleRadius` (80) |
| `quarter-simple-card` | Quarter-circle simple card | `width` (150), `height` (150), `iconSize` (30), `padding` (20), `borderRadius` (16) |
| `rounded-rect-node` | Rounded rectangle node | `width` (300), `height` (40), `padding` (4) |
| `underline-text` | Text with underline | `width` (200), `gap` (4) |

## Built-in Templates (~130)

Templates combine a structure + item(s) + optional theme defaults. Listed by category.

### List Templates

| Template | Structure | Item |
|---|---|---|
| `list-pyramid-rounded-rect-node` | list-pyramid | rounded-rect-node |
| `list-pyramid-badge-card` | list-pyramid | badge-card |
| `list-pyramid-compact-card` | list-pyramid | compact-card |
| `list-column-done-list` | list-column | done-list |
| `list-column-vertical-icon-arrow` | list-column | vertical-icon-arrow |
| `list-column-simple-vertical-arrow` | list-column | simple-vertical-arrow |
| `list-grid-badge-card` | list-grid | badge-card |
| `list-grid-candy-card-lite` | list-grid | candy-card-lite |
| `list-grid-circular-progress` | list-grid | circular-progress |
| `list-grid-compact-card` | list-grid | compact-card |
| `list-grid-done-list` | list-grid | done-list |
| `list-grid-horizontal-icon-arrow` | list-grid | horizontal-icon-arrow |
| `list-grid-progress-card` | list-grid | progress-card |
| `list-grid-ribbon-card` | list-grid | ribbon-card |
| `list-grid-simple` | list-grid | simple |
| `list-row-circular-progress` | list-row | circular-progress |
| `list-row-horizontal-icon-arrow` | list-row | horizontal-icon-arrow |
| `list-row-horizontal-icon-line` | list-row | horizontal-icon-line |
| `list-row-simple-horizontal-arrow` | list-row | simple-horizontal-arrow |
| `list-row-simple-illus` | list-row | simple-illus |
| `list-sector-simple` | list-sector | simple |
| `list-sector-plain-text` | list-sector | plain-text |
| `list-sector-half-plain-text` | list-sector (half) | plain-text |
| `list-waterfall-badge-card` | list-waterfall | badge-card |
| `list-waterfall-compact-card` | list-waterfall | compact-card |

### Sequence Templates

| Template | Structure | Item |
|---|---|---|
| `sequence-steps-badge-card` | sequence-steps | badge-card |
| `sequence-steps-simple` | sequence-steps | simple |
| `sequence-steps-simple-illus` | sequence-steps | simple-illus |
| `sequence-timeline-done-list` | sequence-timeline | done-list |
| `sequence-timeline-plain-text` | sequence-timeline | plain-text |
| `sequence-timeline-rounded-rect-node` | sequence-timeline | rounded-rect-node |
| `sequence-timeline-simple` | sequence-timeline | simple |
| `sequence-timeline-simple-illus` | sequence-timeline | simple-illus |
| `sequence-ascending-steps` | sequence-ascending-steps | l-corner-card |
| `sequence-ascending-stairs-3d-simple` | sequence-ascending-stairs-3d | simple |
| `sequence-ascending-stairs-3d-underline-text` | sequence-ascending-stairs-3d | underline-text |
| `sequence-cylinders-3d-simple` | sequence-cylinders-3d | simple |
| `sequence-snake-steps-compact-card` | sequence-snake-steps | compact-card |
| `sequence-snake-steps-pill-badge` | sequence-snake-steps | pill-badge |
| `sequence-snake-steps-simple` | sequence-snake-steps | simple |
| `sequence-snake-steps-simple-illus` | sequence-snake-steps | simple-illus |
| `sequence-snake-steps-underline-text` | sequence-snake-steps | underline-text |
| `sequence-color-snake-steps-horizontal-icon-line` | sequence-color-snake-steps | horizontal-icon-line |
| `sequence-color-snake-steps-simple-illus` | sequence-color-snake-steps | simple-illus |
| `sequence-pyramid-simple` | sequence-pyramid | simple |
| `sequence-funnel-simple` | sequence-funnel | simple |
| `sequence-roadmap-vertical-plain-text` | sequence-roadmap-vertical | plain-text |
| `sequence-roadmap-vertical-simple` | sequence-roadmap-vertical | simple |
| `sequence-roadmap-vertical-badge-card` | sequence-roadmap-vertical | badge-card |
| `sequence-roadmap-vertical-pill-badge` | sequence-roadmap-vertical | pill-badge |
| `sequence-roadmap-vertical-quarter-circular` | sequence-roadmap-vertical | quarter-circular |
| `sequence-roadmap-vertical-quarter-simple-card` | sequence-roadmap-vertical | quarter-simple-card |
| `sequence-roadmap-vertical-underline-text` | sequence-roadmap-vertical | underline-text |
| `sequence-horizontal-zigzag-simple-illus` | sequence-horizontal-zigzag | simple-illus |
| `sequence-horizontal-zigzag-horizontal-icon-line` | sequence-horizontal-zigzag | horizontal-icon-line |
| `sequence-horizontal-zigzag-plain-text` | sequence-horizontal-zigzag | plain-text |
| `sequence-horizontal-zigzag-simple-horizontal-arrow` | sequence-horizontal-zigzag | simple-horizontal-arrow |
| `sequence-horizontal-zigzag-simple` | sequence-horizontal-zigzag | simple |
| `sequence-horizontal-zigzag-underline-text` | sequence-horizontal-zigzag | underline-text |
| `sequence-zigzag-steps-underline-text` | sequence-zigzag-steps | underline-text |
| `sequence-circle-arrows-indexed-card` | sequence-circle-arrows | indexed-card |
| `sequence-zigzag-pucks-3d-simple` | sequence-zigzag-pucks-3d | simple |
| `sequence-zigzag-pucks-3d-underline-text` | sequence-zigzag-pucks-3d | underline-text |
| `sequence-zigzag-pucks-3d-indexed-card` | sequence-zigzag-pucks-3d | indexed-card |
| `sequence-circular-underline-text` | sequence-circular | underline-text |
| `sequence-circular-simple` | sequence-circular | simple |
| `sequence-filter-mesh-underline-text` | sequence-filter-mesh | underline-text |
| `sequence-filter-mesh-simple` | sequence-filter-mesh | simple |
| `sequence-mountain-underline-text` | sequence-mountain | underline-text |

### Comparison Templates

| Template | Structure | Item |
|---|---|---|
| `compare-swot` | compare-hierarchy-row | letter-card + plain-text |
| `compare-binary-horizontal-simple-fold` | compare-binary-horizontal (fold) | simple |
| `compare-binary-horizontal-underline-text-fold` | compare-binary-horizontal (fold) | underline-text |
| `compare-binary-horizontal-badge-card-fold` | compare-binary-horizontal (fold) | badge-card |
| `compare-binary-horizontal-compact-card-fold` | compare-binary-horizontal (fold) | compact-card |
| `compare-binary-horizontal-simple-arrow` | compare-binary-horizontal (arrow) | simple |
| `compare-binary-horizontal-underline-text-arrow` | compare-binary-horizontal (arrow) | underline-text |
| `compare-binary-horizontal-badge-card-arrow` | compare-binary-horizontal (arrow) | badge-card |
| `compare-binary-horizontal-compact-card-arrow` | compare-binary-horizontal (arrow) | compact-card |
| `compare-binary-horizontal-simple-vs` | compare-binary-horizontal (vs) | simple |
| `compare-binary-horizontal-underline-text-vs` | compare-binary-horizontal (vs) | underline-text |
| `compare-binary-horizontal-badge-card-vs` | compare-binary-horizontal (vs) | badge-card |
| `compare-binary-horizontal-compact-card-vs` | compare-binary-horizontal (vs) | compact-card |
| `compare-hierarchy-left-right-circle-node-pill-badge` | compare-hierarchy-left-right | circle-node + pill-badge |
| `compare-hierarchy-left-right-circle-node-plain-text` | compare-hierarchy-left-right | circle-node + plain-text |
| `compare-hierarchy-row-letter-card-compact-card` | compare-hierarchy-row | letter-card + compact-card |
| `compare-hierarchy-row-letter-card-rounded-rect-node` | compare-hierarchy-row | letter-card + rounded-rect-node |

### Chart Templates

| Template | Structure | Item |
|---|---|---|
| `chart-column-simple` | chart-column | simple |
| `chart-bar-plain-text` | chart-bar | plain-text |
| `chart-line-plain-text` | chart-line | plain-text |
| `chart-pie-simple` | chart-pie | simple |
| `chart-pie-plain-text` | chart-pie | plain-text |
| `chart-pie-plain-text-center` | chart-pie (center) | plain-text |
| `word-cloud-simple` | chart-wordcloud | simple |

### Hierarchy Templates

| Template | Structure | Item |
|---|---|---|
| `hierarchy-tree-simple` | hierarchy-tree | simple |
| `hierarchy-tree-compact-card` | hierarchy-tree | compact-card |
| `hierarchy-tree-pill-badge` | hierarchy-tree | pill-badge |
| `hierarchy-mindmap-simple` | hierarchy-mindmap | simple |
| `hierarchy-mindmap-compact-card` | hierarchy-mindmap | compact-card |
| `hierarchy-structure-simple` | hierarchy-structure | simple |
| `hierarchy-structure-compact-card` | hierarchy-structure | compact-card |

### Relation Templates

| Template | Structure | Item |
|---|---|---|
| `relation-circle-circular-progress` | relation-circle | circular-progress |
| `relation-circle-icon-badge` | relation-circle | icon-badge |
| `relation-network-icon-badge` | relation-network | icon-badge |
| `relation-network-simple-circle-node` | relation-network | simple-circle-node |
| `relation-dagre-flow-simple` | relation-dagre-flow | simple |
| `relation-dagre-flow-compact-card` | relation-dagre-flow | compact-card |
| `relation-dagre-flow-badge-card` | relation-dagre-flow | badge-card |

## Built-in Decorations

| Type | Description |
|---|---|
| `simple-arrow` | Simple arrow connector |
| `text-3d` | 3D text effect |
| `triangle` | Triangle marker |

## API — Querying Templates, Structures, Items

```ts
import {
  getTemplate,
  getTemplates,
  registerTemplate,
  getStructure,
  getStructures,
  registerStructure,
  getItem,
  getItems,
  registerItem,
} from '@antv/infographic';

// List all built-in templates
const allTemplates = getTemplates();

// Get a specific template
const template = getTemplate('list-row-simple-horizontal-arrow');

// List all structures
const allStructures = getStructures();

// List all items
const allItems = getItems();
```
