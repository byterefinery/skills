# Charts

`@mui/x-charts` (Community) and `@mui/x-charts-pro` / `-premium`. Two usage styles: **self-contained** components for common cases, **composition** for custom combinations.

- [Self-contained charts](#self-contained-charts)
- [Composition (v8 component API)](#composition-v8-component-api)
- [Axes](#axes)
- [Series](#series)
- [Tooltip](#tooltip)
- [Legend](#legend)
- [Zoom and pan (Pro)](#zoom-and-pan-pro)
- [Export](#export)
- [Server-side rendering](#server-side-rendering)
- [Theming and localization](#theming-and-localization)

## Self-contained charts

Import per type — simplest option; the component wires axes, tooltip, legend, and plot for its series type:

```tsx
import { BarChart } from '@mui/x-charts/BarChart';
import { LineChart } from '@mui/x-charts/LineChart';
import { PieChart } from '@mui/x-charts/PieChart';
import { ScatterChart } from '@mui/x-charts/ScatterChart';
import { RadarChart } from '@mui/x-charts/RadarChart';       // v8, preview
import { Gauge } from '@mui/x-charts/Gauge';                 // v8: animated
import { SparkLineChart } from '@mui/x-charts/SparkLineChart';

<BarChart
  series={[{ data: [10, 20, 30] }]}          // bar type inferred
  xAxis={[{ data: ['A', 'B', 'C'] }]}
  height={300}                                // required (px) for fixed size
/>;
```

- `width` is optional — omit to fill the available space (parent must have intrinsic dimensions).
- Series `type` is inferred by the component; with composition it must be explicit (see below).

## Composition (v8 component API)

`ChartContainer` = `ChartDataProvider` (series/axes/data context) + `ChartsSurface` (SVG). In v8 the subcomponents are **React components**, not `renderXxx()` functions (the v7 function API is removed):

```tsx
import { ChartContainer } from '@mui/x-charts/ChartContainer';
import { BarPlot } from '@mui/x-charts/BarPlot';
import { LinePlot } from '@mui/x-charts/LinePlot';
import { ChartsXAxis } from '@mui/x-charts/ChartsXAxis';
import { ChartsYAxis } from '@mui/x-charts/ChartsYAxis';
import { ChartsTooltip } from '@mui/x-charts/ChartsTooltip';
import { ChartsLegend } from '@mui/x-charts/ChartsLegend';
import { ChartsGrid } from '@mui/x-charts/ChartsGrid';

<ChartContainer
  series={[
    { type: 'bar', data: [1, 2, 3] },
    { type: 'line', data: [3, 2, 1] },
  ]}
  xAxis={[{ data: ['A', 'B', 'C'] }]}
  yAxis={[{ scaleType: 'linear' }]}
  height={300}
>
  <BarPlot />
  <LinePlot />
  <ChartsXAxis label="X" />
  <ChartsYAxis label="Y" />
  <ChartsTooltip />
</ChartContainer>
```

- Each `<XxxPlot />` renders only series matching its type.
- Render order = SVG paint order (later overlaps earlier). No `z-index` in SVG.
- Clipping: `<ChartsClipPath id={useId()} />` + wrap elements in `<g clipPath={url(#id)}>`.
- `<ChartContainer />` is **responsive by default** (`ResponsiveChartContainer` was removed in v8). Parent must have intrinsic dimensions.
- `disableAxisListener` when you use neither tooltip nor axis highlight (skips mouse tracking).
- Use `ChartDataProvider` + `ChartsSurface` separately when you need HTML components (e.g. a custom legend) between them — see the Legend section.

Available plot/aux components: `LinePlot`, `AreaPlot`, `MarkPlot`, `BarPlot`, `PiePlot` (via `PieChart` internals/composition), `ScatterPlot`, `ChartsXAxis`, `ChartsYAxis`, `ChartsGrid`, `ChartsTooltip`, `ChartsAxisHighlight`, `ChartsReferenceLine`, `ChartsLegend`, `ChartsClipPath`, `ChartsSurface`.

## Axes

Axis config lives on the container: `xAxis`, `yAxis` arrays (multiple axes allowed; reference via `axisId` on series/plot/axis components):

```tsx
xAxis={[
  {
    id: 'x1',
    scaleType: 'band',   // 'band' | 'linear' | 'point' | 'time' | 'log'
    data: ['A', 'B', 'C'],
    min: 0, max: 10,
    label: 'Quarter',
    formatValue: (v) => `$${v}`,
    tickLabel: ...,
  },
]}
```

- `scaleType` — `band` (categorical, default for x on bar), `linear` (numeric), `point`, `time` (needs `scale` with a date adapter from a date library), `log`.
- Multiple axes: give each an `id`; match it in the axis component (`<ChartsXAxis axisId="x1" />`) and in series (`axisId`).
- v8: axis size is decoupled from `margin` — the container computes space for axes; `margin` still defines outer padding.
- Grid lines: `<ChartsGrid />` (or `gridLines` on axis).
- Font sizing props were renamed in v8: `labelFontSize`/`tickFontSize` on axis config (old names removed).
- Axis position is defined in the axis config (`position`), not on the `ChartsXAxis`/`ChartsYAxis` components (which lost their `position` prop in v8).

## Series

Per-series options (in `series` array):

- `data` — array of numbers or objects; `dataset` (flat table) + `value`/`label` keys map series to columns (shared dataset across series).
- `label` — series name (legend/tooltip).
- `color`, `colorBySeries` / per-point `color`.
- Line: `line`, `mark` (`type: 'circle'` etc.), `area` (fill), `uncertainty` (band), `connectNulls`.
- Bar: `stacked` (`'normal' | 'expanded'`), `grouped`, `barSize`, `barGap`, `barRadius`.
- Pie: `innerRadius`, `outerRadius`, `startAngle`, `endAngle`; `value`/`label` per data point.
- Scatter: point shape options, `size` scale.
- `highlightEnabled`, `hide` — per-series display toggles.
- `missingValues: 'zero' | 'span' | 'break'` for gaps in line series.
- Interactions: `onItemClick`, `onItemHover` on the container; per-series handlers too.

## Tooltip

```tsx
<ChartContainer slotTooltip={MyTooltip} slotProps={{ tooltip: { ... } }}>
```

- `<ChartsTooltip />` (composition) or the default tooltip on self-contained charts.
- `slotProps.tooltip.content` — full custom content: `({ series, seriesIndex, dataIndex, item, axisItems }) => ReactNode`.
- Axis highlight follows the tooltip via `<ChartsAxisHighlight />`.

## Legend

v8: the legend is an **HTML element**, not SVG:

- Self-contained: rendered automatically; `hideLegend` prop replaces the old `slotProps.legend.hidden`; `slotProps.legend` for styling/formatter; `legend` position/direction via `slotProps.legend.position` / `.direction`.
- Composition: `<ChartsLegend />` must be inside the Data Provider but **outside** `ChartsSurface` (it is not SVG):

```tsx
<ChartDataProvider ...>
  <ChartsLegend />            {/* HTML, outside SVG */}
  <ChartsSurface>
    <BarPlot />
    <ChartsXAxis />
  </ChartsSurface>
</ChartDataProvider>
```

- `formatter` for custom item text; `direction` (`row`/`column` values changed in v8 — see migration notes), `position`.

## Zoom and pan (Pro)

`LineChartPro`, `BarChartPro`, `ScatterChartPro` (+ `ChartContainerPro`/`ChartDataProviderPro`):

```tsx
<BarChartPro
  xAxis={[{ data: days, scaleType: 'time', zoom: true, zoomOptions: { step: 5, panning: true } }]}
  series={series}
  height={300}
/>;
```

- `zoom: true` on an axis enables wheel zoom, drag pan, pinch.
- `zoomOptions`: `minStart`, `maxEnd`, `step`, `minSpan`, `maxSpan`, `panning`.
- `zoom.filterMode`: `'keep'` (default) or `'discard'` (other axes adapt to visible range).
- Controlled zoom: `zoomModel` / `onZoomChange`.
- `ChartZoomSlider` renders a draggable range slider bound to a zoom axis.

## Export

```tsx
import { ChartsExportProvider } from '@mui/x-charts/ChartsExportProvider';

<ChartsExportProvider>
  <ChartsToolbarPro />  // Pro: image/PDF copy, download
</ChartsExportProvider>
```

- Toolbar: `ChartsToolbarPro` (Pro) with export buttons; Community export via apiRef.
- Programmatic: `apiRef.exportImage('png')`, `apiRef.exportPdf()` from the Charts API (chart root ref), `onBeforeExport` hook for filename options; `copyStyles` for print fidelity.
- PNG export requires canvas; PDF export inlines chart styles.

## Server-side rendering

Charts render on the server when: (1) `width` and `height` are provided (SVG dimensions cannot be computed server-side), and (2) animations are disabled with `skipAnimation` (otherwise the first render is the empty animation state).

## Theming and localization

- Theme augmentation: `import type {} from '@mui/x-charts/themeAugmentation';` then `theme.components.MuiChartsAxis` (ticks, labels), `MuiChartsLegend`, etc.
- `colors` prop on the container sets the palette; default palettes are exported (`colorPalettes`).
- Localization: `ChartsLocalizationProvider` (locale for date/number formatting in axes/tooltips).
- D3 access for custom scales (CommonJS): `import { scaleLinear } from '@mui/x-charts-vendor/d3-scale'`.
