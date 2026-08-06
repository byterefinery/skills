# Styling

regular-table outputs a standard HTML `<table>`, so regular CSS works for basic styling. For data-aware styling, use `addStyleListener()` combined with `getMeta()`.

## Basic CSS

```css
/* Zebra striping by DOM position */
regular-table tr:nth-child(even) td {
  background: rgba(0, 0, 0, 0.05);
}

/* Hover effect */
regular-table td:hover {
  background: rgba(0, 123, 255, 0.1);
}

/* Fixed font */
regular-table {
  font-family: 'Inter', monospace;
  font-size: 13px;
}
```

CSS-only styling operates on DOM position, not data position. As you scroll, `:nth-child(even)` always targets the same DOM row, not the same data row.

## Data-Aware Styling with addStyleListener

`addStyleListener()` registers a callback invoked after every render (scroll, `draw()`, etc.):

```javascript
const unsubscribe = table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    // meta.y is the virtual row index
    td.classList.toggle("zebra", meta.y % 2 === 0);
  }
});

// Later: unsubscribe();
```

### Value-Based Styling

```javascript
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    const value = Number(meta.value);

    if (value < 0) {
      td.classList.add("negative");
    } else if (value > 100) {
      td.classList.add("high");
    } else {
      td.classList.remove("negative", "high");
    }
  }
});
```

### Heatmap Styling

```javascript
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    const value = Number(meta.value);
    const intensity = Math.min(value / 100, 1);
    td.style.backgroundColor = `rgba(255, 0, 0, ${intensity * 0.3})`;
  }
});
```

### Column-Based Styling

```javascript
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    if (meta.x === 2) {
      td.style.fontWeight = "bold";
    }
  }
});
```

## getMeta() Details

`getMeta()` accepts either an `HTMLElement` or a coordinate-like object:

```javascript
// From element
const meta = table.getMeta(tdElement);

// From coordinates
const meta = table.getMeta({ x: 5, y: 10 });
```

Returns `undefined` for non-cell elements (`<tr>`, `<tbody>`, `<table>`, `<regular-table>`).

### Metadata Properties by Cell Type

| Property | body | row_header | column_header | corner |
|---|---|---|---|---|
| `type` | `"body"` | `"row_header"` | `"column_header"` | `"corner"` |
| `x` | ✓ | ✓ | ✓ | ✓ |
| `y` | ✓ | ✓ | — | ✓ |
| `dx`, `dy` | ✓ | — | — | — |
| `column_header_y` | — | — | ✓ | ✓ |
| `row_header_x` | — | ✓ | — | ✓ |
| `value` | ✓ | ✓ | ✓ | ✓ |
| `user` | ✓ | — | — | — |

## Built-in Themes

### material.css

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/regular-table/dist/css/material.css" />
```

Provides:
- Sub-cell scrolling (smooth pixel-level scroll)
- Sticky column and row headers
- Clean Material Design-inspired styling
- Column resize handles
- Hover and selection states

### sub-cell-scrolling.css

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/regular-table/dist/css/sub-cell-scrolling.css" />
```

Standalone CSS for smooth scrolling without the full material theme. Use this when you want custom styling but still need pixel-level scroll precision.

## Custom Styling Patterns

### Conditional Cell Formatting

```javascript
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    if (!meta) continue;

    switch (meta.x) {
      case 0: // ID column
        td.style.color = "#666";
        break;
      case 1: // Name column
        td.style.fontWeight = "500";
        break;
      case 2: // Status column
        if (meta.value === "active") {
          td.style.color = "green";
        } else if (meta.value === "inactive") {
          td.style.color = "red";
        }
        break;
    }
  }
});
```

### Highlighting Selected Rows

```javascript
const selectedRows = new Set();

table.addEventListener("click", (event) => {
  const meta = table.getMeta(event.target);
  if (meta?.y >= 0) {
    selectedRows.toggle(meta.y);
    table.draw();
  }
});

table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    td.classList.toggle("selected", selectedRows.has(meta.y));
  }
});
```

```css
.selected { background-color: rgba(0, 123, 255, 0.15) !important; }
```

### Contenteditable Cells

```javascript
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    td.setAttribute("contenteditable", "true");
  }
});
```

Note: `contenteditable` must be reapplied after each render since cells are recreated during scrolling.

### Header Styling

```javascript
table.addStyleListener(() => {
  for (const th of table.querySelectorAll("thead th")) {
    const meta = table.getMeta(th);
    if (meta) {
      th.style.cursor = "pointer";
      th.addEventListener("click", () => handleSort(meta.x));
    }
  }
});
```

## Performance Tips

- **Minimize DOM queries in style listeners** — `querySelectorAll("td")` runs on every render. Cache results when possible.
- **Use class toggling over inline styles** — `classList.toggle()` is faster than setting `style` properties individually.
- **Avoid creating new functions in style listeners** — inline arrow functions create new closures on every render.
- **Use `unsubscribe()` for temporary listeners** — if a style listener is only needed for a specific operation, remove it when done.
