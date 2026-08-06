# Column Sizing

regular-table auto-sizes columns based on content, but also supports manual width overrides and persistent sizing.

## Auto-Sizing

By default, columns are sized to fit their content on the first render. Subsequent renders reuse measured widths.

```javascript
table.setDataListener(listener);
table.draw();  // columns auto-sized during this render
```

## saveColumnSizes

Save current column width overrides:

```javascript
const sizes = table.saveColumnSizes();
// Returns: { 0: 120, 2: 200, 5: 80 }
// Maps column index (number) to pixel width (number)
```

Only columns with explicit overrides are included in the returned record.

## restoreColumnSizes

Apply previously saved column widths:

```javascript
table.restoreColumnSizes({ 0: 120, 2: 200, 5: 80 });
table.draw();  // re-render with restored widths
```

This is useful for persisting user column preferences:

```javascript
// Save on column resize
table.addEventListener("columnresize", () => {
  localStorage.setItem("column-sizes", JSON.stringify(table.saveColumnSizes()));
});

// Restore on init
const saved = JSON.parse(localStorage.getItem("column-sizes"));
if (saved) {
  table.restoreColumnSizes(saved);
}
```

## resetAutoSize

Force recalculation of column widths on the next `draw()`:

```javascript
// Reset all sizing
table.resetAutoSize();

// Reset specific aspects
table.resetAutoSize({
  auto: true,       // reset auto-measured widths
  override: true,   // reset manual overrides
  indices: true,    // reset column indices
  row_height: true, // reset row height measurement
});

// Reset only auto widths
table.resetAutoSize({ auto: true, override: false, indices: false, row_height: false });
```

After `resetAutoSize()`, call `table.draw()` to trigger recalculation.

## Column Width Internals

The internal `_column_sizes` structure has three arrays:

- **`auto`** — auto-measured widths from content
- **`override`** — manual width overrides (persisted via `saveColumnSizes`)
- **`indices`** — final computed widths used for rendering

Override widths take precedence over auto-measured widths.

## Resizing Columns

With `material.css` theme, column resize handles appear on header borders. Users can drag to resize columns. The new widths are captured in the override map.

```css
/* material.css provides resize handles automatically */
```

## Fixed Width Columns

To enforce a specific column width, use a style listener:

```javascript
table.addStyleListener(() => {
  for (const th of table.querySelectorAll("thead th")) {
    const meta = table.getMeta(th);
    if (meta && meta.x === 0) {
      th.style.width = "50px";
      th.style.minWidth = "50px";
      th.style.maxWidth = "50px";
    }
  }

  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    if (meta && meta.x === 0) {
      td.style.width = "50px";
      td.style.minWidth = "50px";
      td.style.maxWidth = "50px";
    }
  }
});
```

## Hiding Columns

Hide a column by setting its override width to 0:

```javascript
table.restoreColumnSizes({ 3: 0 });  // hide column 3
table.draw();
```

Or via CSS:

```css
regular-table td[data-col="3"],
regular-table th[data-col="3"] {
  display: none;
}
```

Note: hiding columns via CSS does not affect the virtual data model — the column is still fetched and rendered in the DOM, just hidden visually.

## Gotchas

- **`saveColumnSizes()` only saves overrides** — auto-measured widths are not included. Only columns that the user has explicitly resized appear in the saved record.
- **`resetAutoSize()` requires `draw()`** — calling `resetAutoSize()` alone does not trigger a re-render. Call `table.draw()` afterward.
- **Column indices include row headers** — when using row headers, the column index for the first data column is offset by the number of row header columns. Use `meta.size_key` for the absolute index.
- **`restoreColumnSizes()` before `setDataListener`** — you can restore column sizes before setting the data listener, and they will be applied on the first `draw()`.
- **Override widths persist across `setDataListener` calls** — unless `preserve_state: false` (default), manual column width overrides are preserved when re-setting the data listener.
