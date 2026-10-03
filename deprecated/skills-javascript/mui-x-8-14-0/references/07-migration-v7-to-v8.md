# Migration v7 → v8

v8.0.0 (April 2025) is the major from v7. Codemods exist for most renames: `npx @mui/x-codemod` (per-component transforms; run per package). Full guides: `mui.com/x/migration/migration-{data-grid,pickers,tree-view,charts}-v7/`.

## General

- Peer deps: React 17–19 (19 added); `@mui/material@7` supported.
- Package layout: pickers adapter import paths changed (`AdapterDateFns` → `AdapterDateFnsV2` for date-fns v2; v1 adapter renamed too).
- `LicenseInfo` now only from `@mui/x-license` (removed from `x-data-grid-pro`/`-premium` exports).

## Data Grid

**Selection (biggest API break)**

- `rowSelectionModel` / `onRowSelectionModelChange` now use `{ type: 'include' | 'exclude', ids: Set<GridRowId> }` instead of `GridRowId[]`. Use `createRowSelectionManager()` to build/mutate.
- `rowSelectionPropagation` default changed to `{ parents: true, descendants: true }` (group rows).
- `indeterminateCheckboxAction` removed (indeterminate click now selects the unselected descendants).
- `gridRowSelectionManagerSelector` replaces `selectedIdsLookupSelector`; `selectedGridRowsSelector` → `gridRowSelectionIdsSelector`; `selectedGridRowsCountSelector` → `gridRowSelectionCountSelector`.

**Removed / renamed**

- `rowPositionsDebounceMs`, `resetPageOnSortFilter` removed (page always resets to 0 after sort/filter).
- `apiRef.current.resize()` and `forceUpdate()` removed — use selectors + `useGridSelector()`.
- `useGridApiEventHandler` → `useGridEvent`; `useGridApiOptionHandler` → `useGridEventPriority`.
- `unstable_*` stabilized: `unstable_dataSource` → `dataSource`, `unstable_lazyLoading` → `lazyLoading`, `unstable_rowSpanning` → `rowSpanning`, `unstable_listView` → `listView` (+ `listViewColumn`, `GridListViewColDef`).
- `GridToolbar` no longer needed as a slot to show the toolbar — use the `showToolbar` prop; the quick filter is now in the toolbar by default (hide with `slotProps.toolbar.showQuickFilter: false`).
- Density selector removed from the default toolbar (set `density` prop or build a custom toolbar).
- `GridOverlays`, `GridSaveAltIcon`, `sanitizeFilterItemValue`, `GridSortItem` no longer exported.
- `useGridApiRef()` returns a ref initialized to `null` (type includes null).
- `data-*`/`aria-*` props on the component no longer forwarded — use `slotProps.root` / `slotProps.main`.
- Column visibility "Reset" now resets to the initial model, not the panel-open model.

## Date and Time Pickers

- **View selection** — no automatic switch between date/time views or start/end range positions; a "Next" action button moves between them.
- **Field DOM** — new accessible structure: sections are distinct elements; `slotProps.field` and `ownerState` shape changed.
- `ownerState` cleaned up (internal keys removed — update custom slot components reading them).
- Mobile pickers now support field editing.
- Range pickers: new default fields (`SingleInput*RangeField` defaults changed).
- Partially filled fields report `null` in `onChange` until complete.
- `disableOpenPicker` deprecated — use a custom/no `openPicker` slot.
- `closeOnSelect` defaults and action bar `actions` updated.
- Month and Year calendar views changed (new DOM/behavior) — check custom calendars.
- date-fns adapter imports renamed (v1/v2 split).

## Charts

- **Composition API** — `renderXAxis()`/`renderYAxis()`/`renderLine()`/`renderBar()`/`renderTooltip()` functions removed; use `<ChartsXAxis />`, `<ChartsYAxis />`, `<LinePlot />`, `<BarPlot />`, `<ChartsTooltip />` components inside `<ChartContainer />`.
- `ResponsiveChartContainer` removed — `ChartContainer` is responsive by default.
- **Legend is HTML** — `slotProps.legend.hidden` → `hideLegend`; `LegendPosition` → `Position`; legend/direction/position values renamed; legend must be outside `ChartsSurface` in composition.
- Tooltip slots/props renamed and DOM structure updated — update `slotProps.tooltip` and custom tooltip content.
- `ChartsOnAxisClickHandler` removed; `resolveSizeBeforeRender` removed; `experimentalMarkRendering` removed.
- Pie chart axes removed (pie has no axes in v8).
- `useHighlighted` → `useItemHighlighted` / `useItemHighlightedGetter`; `useSeries`/`useXxxSeries` stabilized.
- Axis font props renamed (`labelFontSize`, `tickFontSize`); `topAxis`/`rightAxis`/`bottomAxis`/`leftAxis` props → `position` inside each axis config; `position` removed from `ChartsXAxis`/`ChartsYAxis`.
- `SparkLineChart` `colors` prop renamed.
- `react-spring` dependency removed.

## Tree View

- `TreeView` (the old rich component) removed — use `SimpleTreeView` (JSX) or `RichTreeView` (items).
- `TreeItem2` (+ related utils) renamed to `TreeItem`-family names (the `2` suffix dropped).
- `TreeItem` `ContentComponent`/`ContentProps` removed — use `slots`/`slotProps` and `useTreeItem`.
- `TreeItem` `onClick`/`onMouseDown` now target the item **root**, not the content — use `onItemClick` on the tree for content clicks.
- `publicAPI.selectItem()` renamed; `setItemsExpansion` signature changed; don't call public API methods during render.
- Indentation now applied on the item content instead of the parent group (custom indentation changed).
