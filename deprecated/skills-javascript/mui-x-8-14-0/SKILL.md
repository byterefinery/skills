---
name: mui-x-8-14-0
description: MUI X 8.14.0, the advanced React component suite for data-rich applications. Covers the Data Grid (Community/Pro/Premium with filtering, sorting, row grouping, aggregation, pivoting, Excel export, and the server-side Data Source), Charts (self-contained and composable line, bar, pie, scatter, radar, funnel with zoom and pan), Date and Time Pickers (Day.js, date-fns, Luxon, Moment adapters plus range pickers), and Tree View (simple, rich, drag and drop). Includes open-core licensing, plan upgrades, and license key setup. Use when building React apps with MUI X data grids, charts, date pickers, or tree views, or when migrating from MUI X v7.
license: MIT for Community packages; Pro and Premium packages are under the commercial MUI X license
compatibility: Requires React 17-19 and @mui/material as peer dependency. Pickers additionally need one of dayjs, date-fns, luxon, or moment. A commercial license key removes watermarks on Pro and Premium.
metadata:
  tags:
    - javascript
    - react
    - ui
    - data-grid
    - charts
    - pickers
    - tree-view
---

# mui-x 8.14.0

## Overview

MUI X is a collection of advanced React components for data-rich applications, built on Material UI. It is **open-core**: the base package of each component is MIT-licensed, while advanced features live in paid **Pro** and **Premium** packages. Each plan is a **superset** of the previous one, and each plan ships as a *separate npm package* with its own import path.

| Component | Community (MIT) | Pro (commercial) | Premium (commercial) |
|---|---|---|---|
| Data Grid | `@mui/x-data-grid` — `DataGrid` | `@mui/x-data-grid-pro` — `DataGridPro`: multi-filter/sort, column resize and pin, row reordering, tree data | `@mui/x-data-grid-premium` — `DataGridPremium`: row grouping, aggregation, pivoting, Excel export, AI Assistant |
| Charts | `@mui/x-charts` — `BarChart`, `LineChart`, `PieChart`, `ScatterChart`, `RadarChart` (preview), `Gauge`, `SparkLineChart` | `@mui/x-charts-pro` — `*ChartPro` with zoom and pan, `FunnelChart`, `ChartsToolbarPro` | `@mui/x-charts-premium` |
| Date and Time Pickers | `@mui/x-date-pickers` — Date/Time/DateTime pickers and fields | `@mui/x-date-pickers-pro` — range pickers (`DateRangePicker`, `DateTimeRangePicker`, `TimeRangePicker`) | — |
| Tree View | `@mui/x-tree-view` — `SimpleTreeView`, `RichTreeView` | `@mui/x-tree-view-pro` — `RichTreeViewPro` with drag-and-drop reordering | — |

v8 highlights (stable since 8.0.0, April 2025; this skill targets 8.14.0):

- React 19 support; `@mui/material@7` supported (peer dependency on `@mui/material` remains).
- Data Grid **Data Source** (server-side fetching, pagination, filtering, sorting) is now **Community** — `dataSource` prop plus `dataSourceCache`, `lazyLoading`, `onDataSourceError`.
- Data Grid **Pivoting** (Premium), **AI Assistant** (Premium, `aiAssistant` prop + `GridAiAssistantPanel` slot), header filters, scroll restoration.
- Charts composition is now **React components** (`<ChartsXAxis />`, `<LinePlot />`, …) — the v7 `renderXAxis()` function API is gone. Legends are HTML elements. `ResponsiveChartContainer` was removed; `ChartContainer` is responsive by default. New `RadarChart` (Community, preview) and `FunnelChart` (Pro). SSR under conditions.
- Pickers: no automatic switching between date/time views or between range start/end — a **Next** action button moves views. New `TimeRangePicker` (Pro). New accessible DOM structure for fields.
- Tree View: `TreeItem` customization via `slots`/`slotProps` and the `useTreeItem` hook; automatic parent/children selection on Rich Tree View.

Core concepts common to all components:

1. **Plan-based imports** — upgrading means installing the paid package and replacing all imports (e.g. `@mui/x-data-grid` → `@mui/x-data-grid-pro`). Component names differ per plan (`DataGrid` / `DataGridPro` / `DataGridPremium`).
2. **Material UI peer** — every package has a peer dependency on `@mui/material`; MUI X styling flows from the MUI theme.
3. **Theme augmentation (TypeScript)** — to type `theme.components.MuiDataGrid` (or `MuiXxx`) overrides/defaultProps, import `type {} from '@mui/x-data-grid/themeAugmentation'`.
4. **Data Grid state** — uncontrolled via `initialState`, read via `apiRef` + exported selectors (never raw state), controlled via per-feature model props (`filterModel`, `sortModel`, `paginationModel`, …).

## Usage

### Installation

```bash
npm install @mui/material @emotion/react @emotion/styled
# one package per component, per plan, e.g.:
npm install @mui/x-data-grid @mui/x-charts @mui/x-date-pickers @mui/x-tree-view
# pickers additionally need one date library:
npm install dayjs   # or date-fns, luxon, or moment
```

Set the license key once (Pro/Premium), before the first render, in the browser:

```tsx
import { LicenseInfo } from '@mui/x-license';
LicenseInfo.setLicenseKey('YOUR_LICENSE_KEY');
```

### Data Grid

```tsx
import * as React from 'react';
import { DataGrid, GridRowsProp, GridColDef } from '@mui/x-data-grid';

const columns: GridColDef[] = [
  { field: 'name', headerName: 'Product', width: 200 },
  { field: 'desc', headerName: 'Description', width: 300 },
];
const rows: GridRowsProp = [
  { id: 1, name: 'Data Grid', desc: 'Community' },
  { id: 2, name: 'DataGridPro', desc: 'Pro' },
];

export default function App() {
  return (
    <div style={{ height: 400, width: '100%' }}>
      <DataGrid rows={rows} columns={columns} />
    </div>
  );
}
```

For server data (v8, Community): pass a `dataSource` object with a `getRows()` method instead of manually wiring `rows` plus `*Mode="server"` props. Details in [02-data-grid](references/02-data-grid.md).

### Charts

```tsx
import * as React from 'react';
import { BarChart } from '@mui/x-charts/BarChart';

export default function App() {
  return <BarChart series={[{ data: [10, 20, 30] }]} xAxis={[{ data: ['A', 'B', 'C'] }]} height={300} />;
}
```

For combinations (bar + line on one plot), compose: put `<LinePlot />` / `<BarPlot />` / `<ChartsXAxis />` / `<ChartsYAxis />` / `<ChartsTooltip />` inside `<ChartContainer>` — in v8 these are React components, not render functions.

### Date and Time Pickers

```tsx
import * as React from 'react';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';

export default function App() {
  const [value, setValue] = React.useState<Date | null>(null);
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <DatePicker label="Date" value={value} onChange={(v) => setValue(v)} />
    </LocalizationProvider>
  );
}
```

### Tree View

```tsx
import * as React from 'react';
import { SimpleTreeView } from '@mui/x-tree-view/SimpleTreeView';
import { TreeItem } from '@mui/x-tree-view/TreeItem';

export default function App() {
  return (
    <SimpleTreeView aria-label="Packages">
      <TreeItem label="@mui/x-data-grid" itemId="dg">
        <TreeItem label="Community" itemId="dg-c" />
      </TreeItem>
    </SimpleTreeView>
  );
}
```

Use `RichTreeView` with an `items` array for dynamic data and larger trees.

## Gotchas

- **Parent must have intrinsic dimensions** — Data Grid and Charts render nothing if their parent's size depends on its content. Wrap in a container with explicit height/width (or `100%`).
- **Keep the `columns` prop referentially stable** — the grid treats column definitions as immutable after mount; a new array identity per render risks losing widths and order.
- **Community vs. Pro/Premium pagination defaults** — pagination is on by default in Community (and cannot be disabled) but **off** by default in Pro/Premium. Upgrading a grid to Pro silently loses pagination.
- **Pro/Premium without a license key** — components work but show a watermark and console warnings; a 30-day non-production trial applies, and `NODE_ENV=production` suppresses the watermark for expired keys.
- **License key runs in the browser** — calling `setLicenseKey()` in `next.config.js` or on the server has no effect; it must execute before the first MUI X component mounts.
- **Selectors, not raw state** — never read `apiRef.current.state` directly; use exported selectors (`gridFilterModelSelector(apiRef)`) or `useGridSelector()`. `useGridApiRef()` starts as `null`.
- **v8 selection model shape** — `rowSelectionModel` is `{ type: 'include' | 'exclude', ids: Set<GridRowId> }`, not `GridRowId[]`. Use `gridRowSelectionManagerSelector` / `createRowSelectionManager`.
- **v8 charts composition** — `renderXAxis()`/`renderLine()` functions and `ResponsiveChartContainer` were removed; compose with `<ChartsXAxis />`, `<LinePlot />`, etc. `ChartsLegend` is HTML and must sit inside `ChartDataProvider` but **outside** `ChartsSurface`.
- **Pickers v8 view navigation** — pickers no longer auto-switch between date and time views, or between start/end of a range; the user presses the **Next** action. Code relying on the old automatic behavior breaks UX.
- **One `LocalizationProvider` per app** — wrap the app root once; do not repeat providers per component.
- **`valueGetter`/`renderCell`/`valueSetter` take `(value, row, column, api)`** — the v7+ signature, not `(value)` alone.
- **Data Grid CSS imports need bundler config** — Vite and Next.js App Router work out of the box; Next.js Pages Router needs `transpilePackages`; Vitest needs `test.deps.inline`; Jest needs a CSS mock.
- **`useDemoData` is dev-only** — `@mui/x-data-grid-generator` is not for production; write your own rows.

## References

- [01-installation-licensing](references/01-installation-licensing.md) — package matrix, peer dependencies, bundler setup, license plans, license key, validation failures
- [02-data-grid](references/02-data-grid.md) — Data Grid Community: columns, rows, state, selection, editing, filtering, sorting, pagination, export, server-side Data Source
- [03-data-grid-pro-premium](references/03-data-grid-pro-premium.md) — Pro: multi-filter/sort, pinning, resizing, tree data, row reordering; Premium: row grouping, aggregation, pivoting, Excel export, AI Assistant
- [04-charts](references/04-charts.md) — self-contained and composable charts, axes, series, tooltips, legend, zoom and pan, export, SSR
- [05-pickers](references/05-pickers.md) — adapters, LocalizationProvider, component families, fields, validation, range pickers
- [06-tree-view](references/06-tree-view.md) — SimpleTreeView, RichTreeView, TreeItem customization, lazy loading, drag and drop
- [07-migration-v7-to-v8](references/07-migration-v7-to-v8.md) — v8 breaking changes per component and the upgrade path
