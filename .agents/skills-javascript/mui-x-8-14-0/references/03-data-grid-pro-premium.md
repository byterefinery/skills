# Data Grid Pro and Premium

`DataGridPro` from `@mui/x-data-grid-pro`, `DataGridPremium` from `@mui/x-data-grid-premium`. Both are supersets of Community (see [02-data-grid](02-data-grid.md) for shared API). Import `LicenseInfo` from `@mui/x-license` and set the key once.

## Pro features

### Multi-filtering

Filter items get an `id`; rows match per `logicOperator`:

```tsx
<DataGridPro
  filterModel={{
    items: [
      { id: 1, field: 'rating', operator: '>', value: '4' },
      { id: 2, field: 'isAdmin', operator: 'is', value: 'true' },
    ],
    logicOperator: GridLogicOperator.Or, // or And
  }}
/>;
```

`disableMultiFilters` reverts to single-filter behavior.

### Multi-sorting

Stack multiple `sortModel` entries (Ctrl/Cmd+click on headers); `sortCellMenu` adds sort order actions. Community sorts one column at a time.

### Column resizing

`columnResizeModel` (initial state or controlled), `onColumnResized`, `columnResizeMode` (`'mouse' | 'pixelPerfect'`), `disableColumnResize`.

### Column pinning

```tsx
<DataGridPro pinnedColumns={['name']} pinnedColumnsMode="left" onPinnedColumnsChange={setPinned} />;
```

Modes: `left`, `right`, `both`. Pinning icons appear in column headers and menus.

### Column reordering

Drag headers to reorder; `onColumnOrderChange`, `columnOrder` (controlled), `columnOrderModel` in `initialState`.

### Row reordering

```tsx
<DataGridPro rowReordering onRowReorder={(params) => persist(params.rowId, params.targetIndex)} />;
```

Only visible, non-pinned rows reorder; `getRowId` required for correct ids.

### Row pinning

Pin rows to the top/bottom, independent of pagination and sorting: `pinnedRowModels` (array of row objects), `pinnedRowsMode` (`'left'`/`right`/`both` for column-style pinning of row columns; row pinning uses `pinnedRows` model).

### Tree data

Render hierarchical data from flat rows:

```tsx
<DataGridPro
  treeData
  getTreeDataPath={(row) => row.path /* string[] | null for roots */}
  defaultGroupingExpansionDepth={1}
/>;
```

Group rows expose `isGroup` and children collapse/expand via the row expander. Combine with pagination, filtering, and sorting.

## Premium features

Premium adds everything above plus:

### Row grouping

Group rows by any column:

```tsx
<DataGridPremium
  rowGroupingModel={['name']}
  onRowGroupingModelChange={setRowGroupingModel}
  groupingColDef={{ ... }} // custom expander/summary cell
  disableRowGrouping
/>;
```

- Initial: `initialState={{ rowGrouping: { rowGroupingModel: ['name'] } }}`.
- Drag column headers into the "Row grouping" area (preferences panel) or use the column menu.
- `getGroupedRowId(row, groupColumnField)` for deterministic group ids; `getGroupChildren` / `getGroupRowChildren` for custom grouping.
- Group summary rows show aggregation values (below).

### Aggregation

```tsx
<DataGridPremium
  aggregationModel={{ name: 'sum' }} // field → aggFunc name
  getAggregationPosition={(col) => 'bottom'} // 'top' | 'bottom' | 'auto'
/>;
```

- Built-in functions: `sum`, `avg`, `min`, `max`, `count`, `sumUnique`, `avgUnique`, `minUnique`, `maxUnique`, `countUnique`, `customAggFnc`.
- Custom: `aggregation.getAggregation` / register via `aggregation` prop with `valueGetter`.
- Works on grouped rows, tree data, and (server-side) with the Data Source.

### Pivoting

Cross-tabulation: drag columns into **Rows**, **Columns**, **Values** (with aggregation function) in the pivot panel.

```tsx
<DataGridPremium
  pivotModel={{
    rows: [{ field: 'commodity' }],
    columns: [{ field: 'year', sort: 'asc' }],
    values: [{ field: 'amount', aggFunc: 'sum' }],
  }}
  onPivotModelChange={setPivotModel}
  pivotActive            // boolean: grid shows pivoted data
  pivotPanelOpen
/>;
```

- State: `initialState={{ pivoting: { model, active, panelOpen } }}`.
- Columns must be marked `pivotable` in their `GridColDef` to appear in the panel.
- `disablePivoting` hides the toolbar icon.
- While pivot mode is active these props are ignored: `rows`, `columns`, `rowGroupingModel`, `aggregationModel`, `getAggregationPosition`, `columnVisibilityModel`, `columnGroupingModel`, `groupingColDef`, `headerFilters`, `disableRowGrouping`, `disableAggregation`.

### Excel export

```tsx
apiRef.current.exportDataAsExcel({
  fileName: 'report.xlsx',
  includeColumnHeaders: true,
  allColumns: true, // ignore column visibility
  includeGroupingColumns: true,
  includeHiddenColumns: false,
  getCellData: (colDef, row, colIndex, rowIndex) => ... // custom cell values
  onCellExport: ... // custom XLSXJS cell config (number formats, etc.)
});
```

Large exports run in a Web Worker by default (disable to debug). Requires the key to be valid; serialization performance was improved in v8.

### AI Assistant (preview)

Natural-language queries that return Data Grid API commands:

```tsx
import { GridAiAssistantPanel } from '@mui/x-data-grid-premium/GridAiAssistantPanel';

<DataGridPremium
  aiAssistant={{
    generateCommand: async (prompt) => 'myCommand(...)', // your LLM call
  }}
  slots={{ aiAssistantPanel: GridAiAssistantPanel }}
  slotProps={{ aiAssistantPanel: { generateCommand: myGenerateCommand } }}
/>;
```

The assistant result executes against the grid API (e.g. set filter/sort/pagination models). Wire `generateCommand` to your model endpoint; treat the returned string as code.

### Charts integration (preview)

Dynamic charts driven by grid state: `GridChartsIntegrationContextProvider` + `GridChartsRendererProxy` from `@mui/x-data-grid-premium`, and `ChartRenderer` from `@mui/x-charts-premium`.

## Performance notes (Pro/Premium)

- Row virtualization is on by default; 100k rows × 30 columns is the documented Pro demo scale.
- Keep `columns`/`rows` referentially stable; use `getRowId` for delta updates.
- `pageSizeAuto` (Premium) sizes pages to the viewport.
- `getEstimatedRowHeight` / `getRowHeight` customizations disable some virtualization optimizations — measure before using.
- Scroll restoration (v8): scroll position is restored after state changes; `scrollRestoration`-related props on the scrolling model.
