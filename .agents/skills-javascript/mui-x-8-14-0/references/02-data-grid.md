# Data Grid (Community)

Core `DataGrid` from `@mui/x-data-grid`. Pro/Premium extensions are in [03-data-grid-pro-premium](03-data-grid-pro-premium.md).

- [Rows and columns](#rows-and-columns)
- [Column definition](#column-definition)
- [Rows and updates](#rows-and-updates)
- [Row selection](#row-selection)
- [State and apiRef](#state-and-apiref)
- [Editing](#editing)
- [Filtering](#filtering)
- [Sorting](#sorting)
- [Pagination](#pagination)
- [Theming, slots, classes](#theming-slots-classes)
- [Overlays and localization](#overlays-and-localization)
- [Export](#export)
- [Master-detail](#master-detail)
- [Server-side data (Data Source)](#server-side-data-data-source)

## Rows and columns

The grid requires intrinsic dimensions on its parent (`height` + `width`, e.g. a `100%`-width div with fixed height), otherwise it renders empty.

```tsx
const rows: GridRowsProp = [
  { id: 1, name: 'Data Grid', description: 'the Community version' },
];

const columns: GridColDef[] = [
  { field: 'name', headerName: 'Product', width: 200 },
  { field: 'description', headerName: 'Description', width: 300 },
];

<DataGrid rows={rows} columns={columns} />;
```

- `id` on every row enables delta updates and selection. Without it, a unique `id` field is required or you must provide `getRowId` (row object → id).
- Keep the `columns` array referentially stable across renders (define outside the component or memoize). Column definitions are meant to never change after mount.

## Column definition

`GridColDef` (only `field` is required):

| Prop | Purpose |
|---|---|
| `field` | Column id, matches the row key |
| `headerName` | Header text |
| `type` | `string`, `number`, `boolean`, `date`, `time`, `dateTime` — drives default filter/sort/edit |
| `width`, `minWidth`, `maxWidth`, `flex` | Sizing (`flex` for proportional widths) |
| `valueGetter` | Derive display value: `(value, row, column, api) => ...` (v7+ signature) |
| `valueFormatter` | Format value for display (not used in export) |
| `valueSerializer` | Format value for CSV/Excel export |
| `valueParser` | Parse edited text back to the stored value |
| `renderCell` | Custom cell content: `(params) => ...` (`params.value`, `params.row`, `params.api`) |
| `renderEditCell` | Custom edit component |
| `isEditable` | Allow cell editing (cell edit mode) |
| `sortable`, `filterable` | Per-column feature switches |
| `getApplyQuickFilterFn` | Custom quick-filter logic for this column |
| `columnGroup` | Column group header (nested object for deeper groups) |
| `headerAlign`, `align` | Content alignment |
| `description` | Header tooltip |
| `hide` | Initially hidden |
| `disableColumnMenu` | Hide the column menu |
| `cellClassName`, `headerClassName` | Per-cell / per-header class |
| `pivotable` | Mark the column usable in pivoting (Premium) |

Built-in column types provide default `valueGetter`/`renderCell`/filter operators/sort comparators — override individually as needed.

## Rows and updates

- Delta updates: pass new `rows` array; only rows whose `id` changed re-render.
- `getRowId` — control how rows map to ids.
- Row edit/CRUD flow: use edit mode + `processRowUpdate` (below) or update the `rows` prop yourself after `onRowEditStop`.
- `updateRows` / `upsertRows` apiRef methods mutate rows in place (with `getRowId` support).

## Row selection

```tsx
<DataGrid
  checkboxSelection
  disableRowSelectionOnClick
  selectionModel={selectionModel}
  onRowSelectionModelChange={setSelectionModel}
  isRowSelectable={(row) => row.isActive}
/>;
```

- v8 model shape: `{ type: 'include' | 'exclude', ids: Set<GridRowId> }` (not an array). `exclude` = "all rows except these". Use `createRowSelectionManager({type, ids})` for mutation helpers, or `gridRowSelectionManagerSelector(apiRef)` (exposes `.has(id)`) to read.
- `rowSelectionPropagation` defaults to `{ parents: true, descendants: true }` in v8 (group rows in Pro/Premium). Pass `false` for both to opt out.
- `multiSelect` (default true), `shiftDownClickSelect`, `isRowSelectable`, `disableRowSelectionOnClick`.

## State and apiRef

- `initialState` — same shape as `apiRef.current.exportState()`; only used on mount. Keys include `columns`, `filter`, `sorting`, `pagination`, `selection`, `density`, `pivoting` (Premium), `rowGrouping`, `aggregation`.
- Control features with model props: `filterModel`, `sortModel`, `paginationModel`, `columnVisibilityModel`, `columnOrder`, `selectionModel`, `density`.
- `apiRef = useGridApiRef()` — starts as `null`; use optional chaining or guard. Methods: `getFilteredRows()`, `getVisibleRows()`, `setFilterModel()`, `setColumnVisibilityModel()`, `exportDataAsCsv()`, `print()`, `setCellFocus()`, `rowSelection` helpers, `dataSource` (v8).
- Read state with exported selectors: `gridFilterModelSelector(apiRef)`, `gridSortModelSelector(apiRef)`, `gridPaginationModelSelector(apiRef)`, `gridColumnVisibilitySelector(apiRef)`, … or reactively with `useGridSelector(apiRef, selector)`.
- Subscribe to events: `apiRef.current.subscribeEvent('rowSelectionModelChange', handler)` (v8: `useGridEvent` for hook usage; the old `useGridApiEventHandler` was renamed).

## Editing

Two modes: **cell** (`isCellEditable` per column) and **row** (`processRowUpdate` + `isRowEditable`).

```tsx
<DataGrid
  isCellEditable
  onCellEditCommit={(params) => {
    setRows((rows) =>
      rows.map((r) => (r.id === params.id ? { ...r, [params.field]: params.value } : r)),
    );
  }}
/>;
```

Row mode: `processRowUpdate(newRow, oldRow)` returns the updated row or a rejected edit; returning a `Promise` enables async validation. Stop events: `onRowEditStop`, `onCellEditStop`. Disable stopping on focus-out with `disableStopEditOnCellFocusOut`. Custom edit components via `renderEditCell`.

## Filtering

Filter model: `GridFilterModel = { items: [{ field, operator, value, id? }], logicOperator? }`.

- Community: **single filter only** — the grid filters by one criterion at a time. Multi-filters (AND/OR across items, `id` per item, `logicOperator: GridLogicOperator.And | Or`) require Pro.
- Quick filter in the toolbar filters all columns by default (hide via `slotProps={{ toolbar: { showQuickFilter: false } }}`); per-column `getApplyQuickFilterFn` customizes matching.
- Header filters (v8, Community): rows under the headers using the same operators; toggle with the `headerFilters` prop (default on), disable the default filter panel to keep only inline filters.
- Custom operators: `filterable` column `filterOperators`, or wrap built-ins; custom filter panel via `slots.filterPanel`.
- Server-side without Data Source: `filterMode="server"` + `onFilterModelChange`.

## Sorting

- `sortModel: GridSortItem[]` with `{ field, sort: 'asc' | 'desc' | null }`; `onSortModelChange`.
- Multi-sort (stacking several columns) requires Pro; Community sorts one column at a time.
- `getSortComparator` for custom comparison (per column or grid-wide).
- Server-side: `sortingMode="server"` + `onSortModelChange`.
- Initial sort: `initialState={{ sorting: { sortModel: [{ field: 'name', sort: 'desc' }] } }}`.

## Pagination

- Community: pagination **on by default, cannot be disabled**. Pro/Premium: **off by default** — pass `pagination`.
- Default model `{ page: 0, pageSize: 100 }`; `pageSizeOptions` (default `[100, 500, 1000]`), `rowsPerPageOptions`.
- `paginationMode="server"` + `onPaginationModelChange` for server pagination; `estimatedRowCount` for approximate totals; `pageCount` for a known count.
- Auto page size filling the viewport: `pageSizeAuto` (Premium).
- The v7 `resetPageOnSortFilter` prop is gone — v8 always returns to page 0 after sort/filter.

## Theming, slots, classes

```tsx
import type {} from '@mui/x-data-grid/themeAugmentation'; // enable TS theme augmentation

const theme = createTheme({
  components: {
    MuiDataGrid: {
      defaultProps: { density: 'compact' },
      styleOverrides: { root: { borderRadius: 8 } },
    },
  },
});
```

- `density` — `compact` (40px rows), `standard` (52), `comfortable` (64).
- Row height: `rowHeight`, `getRowHeight`. Full-height grid: `autoHeight` (disables row virtualization).
- Slots: `slots={{ toolbar: MyToolbar, columnsManagement, filterPanel, quickFilter, row, rowDetails, ... }}` with matching `slotProps`. `showToolbar` (v8) renders the default toolbar (column visibility, density menu removed in v8 — add your own via a custom toolbar).
- CSS class names follow MUI conventions: `classes={{ root, headerCell, cell, row, ... }}`.
- v8: `data-*`/`aria-*` props on the component are not forwarded — use `slotProps.root` / `slotProps.main`.
- Default background color was added in v8 theming; align with your `@mui/material` palette or override `.MuiDataGrid-root`.

## Overlays and localization

- Overlays (centered states): `loading` / `error` / no rows — via `slots.loadingOverlay`, `slots.errorOverlay`, `noRowsOverlay`. The v8 **"No columns"** overlay shows when `columns` is empty.
- `hideFooter`, `hideFooterRowCount`, `checkboxSelectionVisibleOnly`.
- Localization: `localeText` (object or function per language), or wrap with Material UI's `LocalizationProvider` — the grid reads MUI's locale text for pagination and other MUI components.

## Export

- CSV: `apiRef.current.exportDataAsCsv({ fieldDelimiter, fileName, includeColumnHeaders, getAllRows })` — exports all data, ignoring pagination by default (`getRowsToExport` customizes which rows).
- Print/PDF: `apiRef.current.print()` (uses the browser print dialog).
- Toolbar export buttons via `GridToolbar` (`exportMode: 'csv' | 'print' | 'csvNoSelection'`), or a custom toolbar slot. Excel export is Premium (see [03](03-data-grid-pro-premium.md)).

## Master-detail

```tsx
<DataGrid
  getDetailPanelContent={(params) => <DetailRow id={params.id} />}
  getDetailPanelHeight={() => 'auto'}
  detailPanelExpandedRowIds={expanded}
  onDetailPanelExpandedRowIdsChange={setExpanded}
/>;
```

`detailPanel` slot for custom rendering; only one expanded panel per column area by default.

## Server-side data (Data Source)

v8: server data is a **Community** feature via the Data Source layer — a single object implementing `getRows`, instead of manual `*Mode="server"` wiring:

```tsx
import { useGridDataSource } from '@mui/x-data-grid';

const dataSource: GridDataSource = {
  getRows: async (params) => {
    const res = await fetch('/api/rows', { method: 'POST', body: JSON.stringify(params) });
    const { rows, total } = await res.json();
    return { rows, rowCount: total }; // GridGetRowsResponse
  },
};

const apiRef = useGridApiRef();
const dataSourceApi = useGridDataSource(apiRef); // optional: manual .getRows(), .updateRow(), .deleteRow()

<DataGrid columns={columns} dataSource={dataSource} pagination showToolbar />;
```

- `params` include `paginationModel`, `sortModel`, `filterModel`, `quickFilter`, plus grouping/aggregation/pivot state when those Premium features are used.
- Caching: `dataSourceCache` (default `defaultDataSourceCache` with LRU + TTL controls; `null` disables).
- `lazyLoading` fetches children/row-group rows on demand; `lazyLoadingRequestThrottleMs` throttles scroll-triggered requests.
- Error handling: `onDataSourceError={(error) => ...}` with `GridGetRowsError` / `GridUpdateRowError` instances (`.params` on get errors).
- Editing with server data: `processRowUpdate` + `dataSourceApi.updateRow()` / `deleteRow()` for delta persistence.
- Legacy pattern (still supported): `rows` prop + `sortingMode="server"` / `filterMode="server"` / `paginationMode="server"` + `on*ModelChange` handlers.
