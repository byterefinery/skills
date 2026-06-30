# Usage

## Browser — Syntax Input (Recommended)

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

## Browser — JS Object Input

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

## Streaming Rendering

The syntax parser is fault-tolerant — render partial output as AI streams tokens:

```ts
let buffer = '';
for (const chunk of aiChunks) {
  buffer += chunk;
  chart.render(buffer);
}
```

## SSR — Server-Side Render to SVG String

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

## Export

```ts
// After render() and in browser
const svgDataUrl = await chart.toDataURL({ type: 'svg' });
const pngDataUrl = await chart.toDataURL({ type: 'png', dpr: 2 });
```

## Events

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

## Update / Destroy

```ts
// Merge new options into existing
chart.update({ data: { lists: newItems } });

// Full replacement
chart.render(newOptions);

// Cleanup
chart.destroy();
```

## Custom Resource Loader

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

## Editor (Built-in)

Set `editable: true` to enable selection, dragging, text editing, and zoom. Default plugins: `EditBar`, `ResizeElement`, `ResetViewBox`. Default interactions: `DragCanvas`, `DblClickEditText`, `BrushSelect`, `ClickSelect`, `DragElement`, `HotkeyHistory`, `ZoomWheel`, `SelectHighlight`.
