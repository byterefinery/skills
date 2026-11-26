# Migration Notes (v3 to v4)

Chart.js 4.6.2 is a v4.x release; these are the breaking changes from the v3 line that matter when porting older code.

## v3 -> v4

**Charts**
- Chart types no longer override the default tooltip callbacks — all types get the same-looking tooltips.
- Defining legacy `xAxes`/`yAxes` in config no longer overrides the default axis — it creates a second scale. Configure scales under `options.scales` keyed by id.

**Options**
- `scales[id].grid.drawBorder` → `scales[id].border.display`; `grid.borderWidth` → `border.width`; `grid.borderColor` → `border.color`; `grid.borderDash` → `border.dash`; `grid.borderDashOffset` → `border.dashOffset`.
- `destroy` plugin hook removed → `afterDestroy`.
- Time scale ticks callback now receives a **timestamp**, not a formatted label.
- Time/timeseries scales use `ticks.stepSize`; `time.stepSize` removed.
- Linear scales add/subtract **5%** of the max value to the range when min == max (was 1).
- Tooltip callback returning `undefined` now falls back to the default callback.
- `maintainAspectRatio` respects container height.
- Legend text/strikethrough no longer falls back to `fontColor`.
- The filler plugin dropped the `config._chart`/`this._chart` fallbacks.

**Distribution / module system**
- Chart.js is an **ESM-only** npm package — your project should be an ES module (`"type": "module"` in package.json); Jest needs ESM config, or use Vitest.
- `dist/chart.js` removed; `dist/chart.min.js` renamed to `dist/chart.umd.min.js`; `dist/chart.esm.js` renamed to `dist/chart.js` (the ESM build).
- The UMD bundle is still available for script tags.

## v2 -> v3 (still relevant for older codebases)

- Dist files are lower case; **no more** `Chart.bundle.js`/`Chart.bundle.min.js` (bundles included moment).
- moment is not an npm dependency of chart.js — time/timeseries scales need an adapter plus its date library.
- The constructor **throws** if the canvas/context is already in use.
- `horizontalBar` chart type removed → `type: 'bar'` + `indexAxis: 'y'`.
- Indexable options loop.
- `elements.rectangle` → `elements.bar`.
- `hover.animationDuration` → `animation.active.duration`; `responsiveAnimationDuration` → `animation.resize.duration`.
- Polar area `elements.arc.angle` in degrees; `startAngle` default 0 (top, degrees, was -π/2).
- Doughnut `rotation` degrees default 0; `circumference` degrees default 360 (was 2π); `cutoutPercentage` → `cutout` (px number or `'%'` string).
- `scale` option removed → `options.scales.r` (or any id with `axis: 'r'`).
- `scales.[x/y]Axes` arrays removed → `options.scales` keyed by scale id.
- Bar sizing moved to dataset options: `barPercentage`, `barThickness`, `categoryPercentage`, `maxBarThickness`, `minBarLength`.
- `scaleLabel` → `scales[id].title`; `scaleLabel.labelString` → `title.text`.
- `ticks.beginAtZero` → `scales[id].beginAtZero`; `ticks.max`/`min`/`reverse` → `scales[id].max`/`min`/`reverse`.
