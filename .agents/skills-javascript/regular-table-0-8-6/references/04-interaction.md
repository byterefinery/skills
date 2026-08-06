# Interaction

regular-table is a standard `HTMLElement`, so DOM events work normally. Combine event listeners with `getMeta()` and `addStyleListener()` for data-aware interactions.

## Click Events

```javascript
table.addEventListener("click", (event) => {
  const meta = table.getMeta(event.target);
  if (meta && meta.type === "body") {
    console.log(`Clicked cell at (${meta.x}, ${meta.y}) = ${meta.value}`);
  }
});
```

## Row Selection

```javascript
const selectedRows = new Set();

table.addEventListener("click", (event) => {
  const meta = table.getMeta(event.target);
  if (meta && meta.y >= 0) {
    if (event.shiftKey && selectedRows.size > 0) {
      // Range selection
      const last = Math.max(...selectedRows);
      const start = Math.min(last, meta.y);
      const end = Math.max(last, meta.y);
      for (let i = start; i <= end; i++) selectedRows.add(i);
    } else if (event.ctrlKey || event.metaKey) {
      // Toggle selection
      if (selectedRows.has(meta.y)) {
        selectedRows.delete(meta.y);
      } else {
        selectedRows.add(meta.y);
      }
    } else {
      // Single selection
      selectedRows.clear();
      selectedRows.add(meta.y);
    }
    table.draw();
  }
});

table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    td.classList.toggle("selected", meta && selectedRows.has(meta.y));
  }
});
```

## Column Selection

```javascript
const selectedColumns = new Set();

table.addEventListener("click", (event) => {
  const meta = table.getMeta(event.target);
  if (meta && meta.type === "column_header") {
    if (selectedColumns.has(meta.x)) {
      selectedColumns.delete(meta.x);
    } else {
      selectedColumns.add(meta.x);
    }
    table.draw();
  }
});

table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    td.classList.toggle("col-selected", meta && selectedColumns.has(meta.x));
  }
});
```

## Keyboard Navigation

```javascript
let focusPos = { x: 0, y: 0 };

table.addEventListener("keydown", (event) => {
  const target = document.activeElement;
  const meta = table.getMeta(target);
  if (!meta) return;

  const numRows = /* total rows */;
  const numCols = /* total columns */;

  switch (event.key) {
    case "ArrowUp":
      event.preventDefault();
      focusPos.y = Math.max(0, meta.y - 1);
      break;
    case "ArrowDown":
      event.preventDefault();
      focusPos.y = Math.min(numRows - 1, meta.y + 1);
      break;
    case "ArrowLeft":
      event.preventDefault();
      focusPos.x = Math.max(0, meta.x - 1);
      break;
    case "ArrowRight":
      event.preventDefault();
      focusPos.x = Math.min(numCols - 1, meta.x + 1);
      break;
    case "Tab":
      event.preventDefault();
      if (event.shiftKey) {
        focusPos.x = Math.max(0, meta.x - 1);
      } else {
        focusPos.x = Math.min(numCols - 1, meta.x + 1);
      }
      break;
    case "Enter":
      event.preventDefault();
      target.setAttribute("contenteditable", "true");
      target.focus();
      return;
  }

  // Scroll to keep focused cell visible
  table.scrollToCell(focusPos.x, focusPos.y);
  table.draw();
});

// Re-apply focus after render
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    if (meta.x === focusPos.x && meta.y === focusPos.y) {
      td.focus();
    }
  }
});
```

## Contenteditable Cells

```javascript
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    td.setAttribute("contenteditable", "true");
  }
});

// Save on blur
table.addEventListener("focusout", (event) => {
  if (event.target.tagName === "TD") {
    const meta = table.getMeta(event.target);
    if (meta) {
      DATA[meta.x][meta.y] = event.target.textContent;
      table.draw();
    }
  }
});

// Save on Enter
table.addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    const target = document.activeElement;
    if (target.tagName === "TD") {
      const meta = table.getMeta(target);
      if (meta) {
        DATA[meta.x][meta.y] = target.textContent;
        target.blur();
        table.draw();
      }
    }
  }
});
```

## Double-Click Editing

```javascript
table.addEventListener("dblclick", (event) => {
  const meta = table.getMeta(event.target);
  if (meta && meta.type === "body") {
    event.target.setAttribute("contenteditable", "true");
    event.target.focus();
  }
});
```

## Context Menu

```javascript
table.addEventListener("contextmenu", (event) => {
  event.preventDefault();
  const meta = table.getMeta(event.target);
  if (meta && meta.type === "body") {
    showContextMenu(event.clientX, event.clientY, meta);
  }
});
```

## Drag Selection (Area Selection)

```javascript
let isDragging = false;
let dragStart = null;
let selectedCells = new Set();

table.addEventListener("mousedown", (event) => {
  const meta = table.getMeta(event.target);
  if (meta && meta.type === "body") {
    isDragging = true;
    dragStart = { x: meta.x, y: meta.y };
  }
});

table.addEventListener("mousemove", (event) => {
  if (!isDragging) return;
  const meta = table.getMeta(event.target);
  if (!meta || meta.type !== "body") return;

  selectedCells.clear();
  const x0 = Math.min(dragStart.x, meta.x);
  const x1 = Math.max(dragStart.x, meta.x);
  const y0 = Math.min(dragStart.y, meta.y);
  const y1 = Math.max(dragStart.y, meta.y);

  for (let x = x0; x <= x1; x++) {
    for (let y = y0; y <= y1; y++) {
      selectedCells.add(`${x},${y}`);
    }
  }
  table.draw();
});

table.addEventListener("mouseup", () => {
  isDragging = false;
});

table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    if (meta) {
      td.classList.toggle("area-selected",
        selectedCells.has(`${meta.x},${meta.y}`));
    }
  }
});
```

## Scroll Events

```javascript
table.addEventListener("scroll", () => {
  // Called on every scroll. Use sparingly as it fires frequently.
  const table = event.target;
  // Save current edit state if needed
  const activeCell = document.activeElement;
  if (activeCell && activeCell.tagName === "TD") {
    const meta = table.getMeta(activeCell);
    if (meta) {
      DATA[meta.x][meta.y] = activeCell.textContent;
    }
  }
});
```

## Event Delegation

Since cells are recreated during scrolling, always use event delegation on the `<regular-table>` element rather than attaching listeners to individual cells:

```javascript
// Good: delegation on the table element
table.addEventListener("click", (event) => {
  const meta = table.getMeta(event.target);
  // ...
});

// Bad: attaching to individual cells (lost on scroll)
for (const td of table.querySelectorAll("td")) {
  td.addEventListener("click", () => { /* lost on next scroll */ });
}
```

## Gotchas

- **`getMeta()` returns `undefined` for non-cell targets** — always check the return value. Clicks on `<tr>`, `<tbody>`, or empty space return `undefined`.
- **Event listeners on cells are lost during scroll** — cells are recreated when scrolling. Always delegate events to the `<regular-table>` element.
- **`contenteditable` must be reapplied after render** — use `addStyleListener()` to set `contenteditable` on every render cycle.
- **`scrollToCell()` is async** — await the call if subsequent code depends on the scroll position.
- **Keyboard events need `tabindex`** — the `<regular-table>` element has `tabindex="0"` set automatically, making it focusable.
