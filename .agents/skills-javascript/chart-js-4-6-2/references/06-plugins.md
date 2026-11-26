# Plugins

Plugins are the main way to customize or change default chart behavior. They can be global (registered once, applied to all charts) or per-chart (passed in the config).

## Using Plugins

```js
const plugin = { /* plugin implementation */ };

// per-chart plugins (also shareable between instances)
const chart1 = new Chart(ctx, { plugins: [plugin] });

// inline plugin (defined in config; NOT registered)
const chart2 = new Chart(ctx, {
  plugins: [{
    beforeInit: function(chart, args, options) { /* .. */ }
  }]
});
```

Global registration:

```js
Chart.register({ /* plugin implementation */ });
```

Inline plugins cannot be registered globally; some plugins require registration and cannot be used inline.

## Plugin ID and Options

Plugin ids follow the npm package name convention: no leading dot/underscore, URL-safe characters, no uppercase, short but descriptive. Public plugins should be prefixed `chartjs-plugin-` and checked against the npm registry.

Plugin options live under `options.plugins.<plugin-id>`. A plugin can declare defaults in its `defaults` entry.

Disable one plugin for an instance: `options.plugins.<id> = false`. Disable all: `options.plugins = false`.

TypeScript users can augment types via declaration merging on `PluginOptionsByType` in a `.d.ts` that declares module `'chart.js'`.

## Hook Lifecycle

Hooks available (verified in the 4.6.2 source): `beforeInit`, `afterInit`, `beforeUpdate`, `afterUpdate`, `beforeLayout`, `afterLayout`, `beforeRender`, `afterRender`, `beforeDraw`, `afterDraw`, `beforeDatasetsDraw`, `beforeDatasetDraw`, `afterDatasetDraw`, `afterDatasetsDraw`, `beforeEvent`, `afterEvent`, `beforeDestroy`, `afterDestroy`.

- The old `destroy` hook was deprecated in 3.7 and **removed in v4** — use `afterDestroy`.
- Most `before*` hooks are cancelable: return `false` to cancel that part of the render pipeline.
- After an event, set `args.changed = true` to request a re-render (the built-in tooltip plugin does this).

## Built-in Plugins

### Legend

Namespace `options.plugins.legend` (defaults in `Chart.defaults.plugins.legend`).

| Name | Default | Description |
|---|---|---|
| `display` | true | Show the legend |
| `position` | 'top' | 'top', 'left', 'bottom', 'right', 'chartArea' (chartArea = left middle, not further configurable) |
| `align` | 'center' | 'start', 'center', 'end' |
| `maxHeight` / `maxWidth` | | Pixel limits |
| `fullSize` | true | Box takes full width/height, moving other boxes |
| `onClick` / `onHover` / `onLeave` | | Callbacks `(event, legendItem, legend)` |
| `reverse` | false | Show datasets in reverse order |
| `labels` | | Label configuration (below) |
| `rtl` / `textDirection` | | Right-to-left rendering / force `'rtl'`/`'ltr'` |
| `title` | | Legend title configuration (below) |

Legend labels (`options.plugins.legend.labels`): `boxWidth` (40), `boxHeight` (font.size), `color`, `font`, `padding` (10), `generateLabels` (function), `filter` (function), `sort` (function matching Array.prototype.sort semantics), `pointStyle` ('circle'), `textAlign` ('center'), `usePointStyle` (false), `pointStyleWidth`, `useBorderRadius` (false), `borderRadius`.

Legend title (`options.plugins.legend.title`): `color`, `display` (false), `font`, `padding` (0), `text`.

The doughnut, pie, and polarArea charts **override legend defaults** — change them with `Chart.overrides.<type>.plugins.legend`.

### Title

Namespace `options.plugins.title` (defaults in `Chart.defaults.plugins.title`).

| Name | Default | Description |
|---|---|---|
| `display` | false | Show the title |
| `text` | '' | string or string[] (multiple lines) |
| `position` | 'top' | top/left/bottom/right |
| `align` | 'center' | start/center/end |
| `font` | {weight: 'bold'} | Font |
| `padding` | 10 | Only top/bottom implemented |
| `color` | Chart.defaults.color | Text color |
| `fullSize` | true | Box sizing |

### Subtitle

Same options as title; namespace `options.plugins.subtitle` (defaults `Chart.defaults.plugins.subtitle`). Placed under the main title by default.

### Tooltip

Namespace `options.plugins.tooltip` (defaults `Chart.defaults.plugins.tooltip`).

| Name | Default | Description |
|---|---|---|
| `enabled` | true | Enable on-canvas tooltips |
| `external` | null | Custom external tooltip function |
| `mode` | interaction.mode | Which elements appear |
| `intersect` | interaction.intersect | Mode applies only on intersection |
| `position` | 'average' | 'average' or 'nearest' (custom modes possible) |
| `callbacks` | | See below |
| `itemSort` / `filter` | | Sort/filter tooltip items |
| `backgroundColor` | 'rgba(0, 0, 0, 0.8)' | |
| `titleColor` / `bodyColor` / `footerColor` | '#fff' | |
| `titleFont` / `bodyFont` / `footerFont` | bold / {} / bold | Default from Chart.defaults.font; overriding requires a function returning a font object |
| `titleAlign` / `bodyAlign` / `footerAlign` | 'left' | left/right/center |
| `titleSpacing` / `bodySpacing` / `footerSpacing` | 2 | |
| `titleMarginBottom` / `footerMarginTop` | 6 | |
| `padding` | 6 | |
| `caretPadding` / `caretSize` | 2 / 5 | |
| `cornerRadius` | 6 | number or object |
| `multiKeyBackground` | '#fff' | |
| `displayColors` | true | Color boxes |
| `boxWidth` / `boxHeight` | bodyFont.size | |
| `boxPadding` | 1 | |
| `usePointStyle` | false | Use dataset point styles instead of boxes |
| `borderColor` / `borderWidth` | 'rgba(0, 0, 0, 0)' / 0 | |
| `rtl` / `textDirection` | | |
| `xAlign` / `yAlign` | undefined | Caret position (left/center/right, top/center/bottom) |

Tooltip callbacks (`options.plugins.tooltip.callbacks`): `beforeTitle`, `title`, `afterTitle`, `beforeBody`, `beforeLabel`, `label`, `labelColor`, `labelTextColor`, `labelPointStyle`, `afterLabel`, `afterBody`, `beforeFooter`, `footer`, `afterFooter`. Title/body/footer ones receive `TooltipItem[]`; label-level ones receive a single `TooltipItem` (overridable per dataset via `data.datasets[].tooltip.callbacks`). Returning `undefined` falls back to the default callback (v4); returning an empty string removes the line. Arrays of strings render as multiple lines.

For HTML tooltips/legends, use the `external` option / custom legend patterns (samples: tooltip/html, legend/html).
