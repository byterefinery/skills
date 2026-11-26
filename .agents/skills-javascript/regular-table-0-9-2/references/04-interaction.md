# Interaction

`<regular-table>` is a normal `HTMLElement` — it is focusable (the element sets `tabindex="0"` when connected), so standard DOM event APIs work alongside the regular-table API. The element also dispatches a `regular-table-scroll` CustomEvent after each processed scroll.

## Clicks and getMeta

```javascript
table.addEventListener("click", (event) => {
  const meta = table.getMeta(event.target);
  if (meta && meta.type === "body") {
    // meta.x / meta.y are the virtual coordinates
  }
});
```

`event.target` may be a child node (a text node, the resize handle span, or a header level), so `getMeta()` can return `undefined` — guard it. The `column_mouse_selection` demo walks `event.path` to find an ancestor with metadata when the direct target has none.

## Row Selection (row_mouse_selection demo)

- Clicking a cell or its row header selects that row; group headers select the whole group.
- `ctrl`/`metaKey` enables multi-selection; a plain click clears the other selections.
- Selection state is re-applied by a `StyleListener` so it survives scrolling (cells are recycled).

## Column and Area Selection

- **column_mouse_selection** — click a column header (with the `event.path` fallback for cells) to select the column; a style listener re-applies the selected class on every render.
- **area_mouse_selection** — rectangular drag selection across cells, tracked as `{x0, x1, y0, y1}` rectangles.
- **area_clipboard** — adds copy/paste/cut to area selection: a `keydown` handler intercepts `ctrl`/`meta` + C/V/X (keyCodes 67/86/88); copy serializes the selection as TSV (cells joined with `\t`, rows with `\n`) and writes it via `navigator.clipboard.writeText()`. Selected data is re-read by calling the `DataListener` directly (`dl(x0, y0, x1 + 1, y1 + 1)`).

## Editable Cells (spreadsheet pattern)

From `examples/spreadsheet`:

- A style listener sets `contenteditable` on every `<td>` — cells are recycled, so the attribute must be re-applied on every render.
- Commit on blur: `write(active_cell)` reads `getMeta(cell)`, writes `DATA[meta.x][meta.y] = text`, then calls `table.draw()`.
- Enter (`keypress` keyCode 13) commits and moves down; Shift+Enter moves up. Arrow keys and Tab navigate via `keydown` codes 9 (Tab), 37/38/39/40 (arrows).
- The selected position is tracked in *virtual* coordinates (`SELECTED_POSITION`) and re-focused by a style listener after each render, so the selection survives scrolling.
- `scrollToCell()` moves the viewport for distant navigation (with a small scroll-ahead buffer) before the focus is restored.
- Commit any in-progress edit on `scroll` and `focusout` so a virtual re-render does not clobber a cell mid-edit.

## Column Resize and Reset

Each column header `<th>` contains a `<span class="rt-column-resize">` drag handle (the material theme styles it with `cursor: col-resize`).

- **Drag** the handle to override that column's width; the drag clamps to a 1px minimum (`Math.max(1, width + diff)`).
- **Double-click** the handle to reset that column's size — double-click is emulated in JavaScript (two `mousedown` events within 500ms), not the native `dblclick` event.
- **Shift + double-click** the handle to reset all column sizes (override, auto, and indices maps).

Columns narrower than their auto width are clamped via generated width rules plus the `rt-cell-clip` class; clipped cells are tagged `rt-col-{size_key}` so the clamp reaches them (unless `column_classes` is on, in which case they already carry the tag).
