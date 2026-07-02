# Plugins Reference

## Built-in Plugins

### Legend

Namespace: `options.plugins.legend`

| Property | Type | Default | Description |
|---|---|---|---|
| `display` | `boolean` | `true` | Show legend |
| `position` | `string` | `'top'` | `'top'`, `'left'`, `'bottom'`, `'right'`, `'chartArea'` |
| `align` | `string` | `'center'` | `'start'`, `'center'`, `'end'` |
| `maxHeight` | `number` | | Max height in px |
| `maxWidth` | `number` | | Max width in px |
| `fullSize` | `boolean` | `true` | Take full chart width/height |
| `reverse` | `boolean` | `false` | Reverse dataset order |
| `onClick` | `function` | | Click handler: `(event, legendItem, legend)` |
| `onHover` | `function` | | Hover handler |
| `onLeave` | `function` | | Leave handler |
| `rtl` | `boolean` | | Right-to-left rendering |
| `textDirection` | `string` | | Force `'rtl'` or `'ltr'` |

#### Legend Labels

Namespace: `options.plugins.legend.labels`

| Property | Type | Default | Description |
|---|---|---|---|
| `color` | `Color` | | Label text color |
| `boxWidth` | `number` | `40` | Color box width |
| `boxHeight` | `number` | `font.size` | Color box height |
| `padding` | `number` | `10` | Padding between rows |
| `font` | `Font` | | Label font |
| `generateLabels` | `function` | | Custom label generator |
| `filter` | `function` | `null` | Filter items: `(legendItem, data) => boolean` |
| `sort` | `function` | `null` | Sort items: `(a, b, data) => number` |
| `usePointStyle` | `boolean` | `false` | Use point style instead of box |
| `pointStyle` | `string` | `'circle'` | Point style for legend |
| `pointStyleWidth` | `number` | `null` | Width of point style |
| `useBorderRadius` | `boolean` | `false` | Use border radius from dataset |
| `textAlign` | `string` | `'center'` | `'left'`, `'right'`, `'center'` |

#### Legend Title

Namespace: `options.plugins.legend.title`

| Property | Type | Default | Description |
|---|---|---|---|
| `display` | `boolean` | `false` | Show title |
| `text` | `string` | | Title text |
| `color` | `Color` | | Title color |
| `font` | `Font` | | Title font |
| `padding` | `number` \| `Padding` | `0` | Padding around title |

#### Hiding Datasets via Legend

```javascript
// Toggle dataset visibility on legend click
onClick: function(event, legendItem, legend) {
  const index = legendItem.datasetIndex;
  const chart = legend.chart;
  const meta = chart.getDatasetMeta(index);
  meta.hidden = !meta.hidden;
  chart.update();
}
```

### Tooltip

Namespace: `options.plugins.tooltip`

| Property | Type | Default | Description |
|---|---|---|---|
| `enabled` | `boolean` | `true` | Show tooltips |
| `mode` | `string` | `interaction.mode` | `'nearest'`, `'index'`, `'dataset'`, `'point'`, `'x'`, `'y'` |
| `intersect` | `boolean` | `interaction.intersect` | Only trigger on intersect |
| `position` | `string` | `'average'` | `'average'` or `'nearest'` |
| `backgroundColor` | `Color` | `'rgba(0, 0, 0, 0.8)'` | Background |
| `titleColor` | `Color` | `'#fff'` | Title color |
| `bodyColor` | `Color` | `'#fff'` | Body color |
| `footerColor` | `Color` | `'#fff'` | Footer color |
| `titleFont` | `Font` | `{weight: 'bold'}` | Title font |
| `bodyFont` | `Font` | `{}` | Body font |
| `footerFont` | `Font` | `{weight: 'bold'}` | Footer font |
| `padding` | `number` \| `Padding` | `6` | Internal padding |
| `caretSize` | `number` | `5` | Arrow size |
| `caretPadding` | `number` | `2` | Arrow padding |
| `cornerRadius` | `number` \| `object` | `6` | Corner radius |
| `displayColors` | `boolean` | `true` | Show color boxes |
| `boxWidth` | `number` | `bodyFont.size` | Color box width |
| `boxHeight` | `number` | `bodyFont.size` | Color box height |
| `boxPadding` | `number` | `1` | Box-to-text padding |
| `usePointStyle` | `boolean` | `false` | Use point style |
| `borderColor` | `Color` | `'rgba(0, 0, 0, 0)'` | Border color |
| `borderWidth` | `number` | `0` | Border width |
| `callbacks` | `object` | | Tooltip callbacks |
| `filter` | `function` | | Filter items |
| `itemSort` | `function` | | Sort items |
| `external` | `function` | `null` | Custom tooltip renderer |
| `xAlign` | `string` | | `'left'`, `'center'`, `'right'` |
| `yAlign` | `string` | | `'top'`, `'center'`, `'bottom'` |

#### Tooltip Callbacks

```javascript
callbacks: {
  title(items) {
    return items[0]?.label || '';
  },
  label(item) {
    return `${item.dataset.label}: ${item.formattedValue}`;
  },
  labelSuffix(item) {
    return ' units';
  },
  beforeBody(items) {
    return 'Summary:';
  },
  afterBody(items) {},
  beforeTitle(items) {},
  afterTitle(items) {},
  beforeFooter(items) {},
  afterFooter(items) {},
  footer(items) {
    return `Total: ${items.reduce((sum, i) => sum + i.raw, 0)}`;
  }
}
```

#### External Tooltip

Render tooltip as HTML element:

```javascript
external: function(context) {
  const tooltipEl = document.getElementById('chartjs-tooltip');
  if (!tooltipEl) return;

  const model = context.opacity;
  tooltipEl.style.opacity = model;
  tooltipEl.style.position = 'absolute';
  tooltipEl.style.left = context.chart.canvas.offsetLeft + context.caretX + 'px';
  tooltipEl.style.top = context.chart.canvas.offsetTop + context.caretY + 'px';
  tooltipEl.style.pointerEvents = 'none';

  if (context.body) {
    tooltipEl.innerHTML = context.body.map(b => b.lines.join('<br>')).join('<br>');
  }
}
```

### Title

Namespace: `options.plugins.title`

| Property | Type | Default | Description |
|---|---|---|---|
| `display` | `boolean` | `false` | Show title |
| `text` | `string` \| `string[]` | | Title text (array = multiline) |
| `color` | `Color` | | Text color |
| `font` | `Font` | | Title font |
| `padding` | `number` \| `Padding` | `{top: 10, bottom: 10}` | Padding |
| `position` | `string` | `'top'` | `'top'`, `'left'`, `'bottom'`, `'right'` |
| `align` | `string` | `'center'` | `'start'`, `'center'`, `'end'` |
| `maxWidth` | `number` | | Maximum width |
| `fullSize` | `boolean` | `true` | Take full width |

### Decimation

Namespace: `options.plugins.decimation`

Automatically reduces data points for performance. Activates when dataset has >1000 points.

| Property | Type | Default | Description |
|---|---|---|---|
| `algorithm` | `string` | `'min-max'` | `'min-max'`, `'lttb'`, `'false'` (disabled) |
| `enabled` | `boolean` | `false` | Force enable |
| `threshold` | `number` | `1000` | Minimum points to trigger |

## Custom Plugins

### Plugin Interface

```javascript
const myPlugin = {
  id: 'my-plugin',

  // Optional: before chart is created
  beforeRegister(chart) {},

  // Optional: after chart is created
  afterRegister(chart) {},

  // Optional: before chart is initialized
  beforeInit(chart, args, options) {},

  // Optional: after chart is initialized
  afterInit(chart, args, options) {},

  // Optional: before chart is updated
  beforeUpdate(chart, args, options) {},

  // Optional: after chart is updated
  afterUpdate(chart, args, options) {},

  // Optional: before elements are drawn
  beforeDatasetsDraw(chart, args, options) {},

  // Optional: after elements are drawn
  afterDatasetsDraw(chart, args, options) {},

  // Optional: before dataset is drawn
  beforeDatasetDraw(chart, args, options) {},

  // Optional: after dataset is drawn
  afterDatasetDraw(chart, args, options) {},

  // Optional: before chart is drawn
  beforeDraw(chart, args, options) {},

  // Optional: after chart is drawn
  afterDraw(chart, args, options) {},

  // Optional: before resize
  beforeResize(chart, args, options) {},

  // Optional: after resize
  afterResize(chart, args, options) {},

  // Optional: before event
  beforeEvent(chart, args, options) {},

  // Optional: after event
  afterEvent(chart, args, options) {},

  // Optional: before chart is destroyed
  destroy(chart, args, options) {}
};
```

### Plugin Args

Each hook receives `(chart, args, options)` where:

- `chart` — the chart instance
- `args` — context-specific arguments (e.g., `{mode}` for update, `{event}` for events)
- `options` — plugin options from `options.plugins['my-plugin']`

### Usage

**Per-chart (inline):**

```javascript
new Chart(ctx, {
  type: 'bar',
  data: { /* ... */ },
  plugins: [myPlugin]
});
```

**Global:**

```javascript
Chart.register(myPlugin);
```

**Disable for specific chart:**

```javascript
new Chart(ctx, {
  options: {
    plugins: {
      'my-plugin': false
    }
  }
});
```

**Plugin options:**

```javascript
new Chart(ctx, {
  options: {
    plugins: {
      'my-plugin': {
        someOption: true
      }
    }
  }
});
```

### Common Plugin Patterns

**Watermark:**

```javascript
{
  id: 'watermark',
  afterDraw(chart) {
    const { ctx, chartArea } = chart;
    ctx.save();
    ctx.font = '20px sans-serif';
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.textAlign = 'center';
    const cx = chartArea.left + chartArea.width / 2;
    const cy = chartArea.top + chartArea.height / 2;
    ctx.fillText('DRAFT', cx, cy);
    ctx.restore();
  }
}
```

**Click handler:**

```javascript
{
  id: 'click-handler',
  afterEvent(chart, args) {
    if (args.event.type === 'click') {
      const points = chart.getElementsAtEventForMode(
        args.event, 'nearest', { intersect: true }, false
      );
      if (points.length) {
        console.log('Clicked:', points[0].element);
      }
    }
  }
}
```

**Custom legend in HTML:**

```javascript
{
  id: 'html-legend',
  afterDraw(chart) {
    const legendContainer = document.getElementById('legend');
    if (!legendContainer) return;
    legendContainer.innerHTML = '';
    chart.data.datasets.forEach((ds, i) => {
      const meta = chart.getDatasetMeta(i);
      const item = document.createElement('div');
      item.style.display = 'inline-block';
      item.style.marginRight = '10px';
      item.innerHTML = `<span style="background:${ds.backgroundColor};width:12px;height:12px;display:inline-block;margin-right:4px;border-radius:2px;"></span>${ds.label}`;
      item.onclick = () => {
        meta.hidden = !meta.hidden;
        chart.update();
      };
      legendContainer.appendChild(item);
    });
  }
}
```
