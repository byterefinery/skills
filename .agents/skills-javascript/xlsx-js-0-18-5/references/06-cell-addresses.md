# Cell Addresses, Ranges, and Coordinate Utilities

## Coordinate System

SheetJS uses **0-indexed** coordinates internally:

| Concept | 0-indexed | A1 notation |
|---|---|---|
| First cell | `{ r: 0, c: 0 }` | `A1` |
| Column B, Row 3 | `{ r: 2, c: 1 }` | `B3` |
| Column AA, Row 1 | `{ r: 0, c: 26 }` | `AA1` |
| Column XFD, Row 1048576 | `{ r: 1048575, c: 16383 }` | `XFD1048576` |

Excel limits: 1,048,576 rows (0–1,048,575) × 16,384 columns (0–16,383, A–XFD).

## Encode Functions

### `encode_cell({ r, c })`

Convert 0-indexed row/column to A1 address string.

```js
XLSX.utils.encode_cell({ r: 0, c: 0 });   // "A1"
XLSX.utils.encode_cell({ r: 2, c: 1 });   // "B3"
XLSX.utils.encode_cell({ r: 0, c: 26 });  // "AA1"
XLSX.utils.encode_cell({ r: 0, c: 701 }); // "AAA1"
```

### `encode_row(row)`

Convert 0-indexed row number to A1 row string.

```js
XLSX.utils.encode_row(0);    // "1"
XLSX.utils.encode_row(99);   // "100"
```

### `encode_col(col)`

Convert 0-indexed column number to A1 column string.

```js
XLSX.utils.encode_col(0);    // "A"
XLSX.utils.encode_col(25);   // "Z"
XLSX.utils.encode_col(26);   // "AA"
XLSX.utils.encode_col(701);  // "AAA"
XLSX.utils.encode_col(16383);// "XFD"
```

### `encode_range(start, end)`

Convert two 0-indexed cell addresses to a range string.

```js
XLSX.utils.encode_range({ r: 0, c: 0 }, { r: 9, c: 3 });  // "A1:D10"
XLSX.utils.encode_range({ s: { r: 0, c: 0 }, e: { r: 9, c: 3 } }); // "A1:D10"
```

## Decode Functions

### `decode_cell(address)`

Convert A1 address to 0-indexed `{ r, c }`.

```js
XLSX.utils.decode_cell("A1");   // { r: 0, c: 0 }
XLSX.utils.decode_cell("B3");   // { r: 2, c: 1 }
XLSX.utils.decode_cell("AA1");  // { r: 0, c: 26 }
```

### `decode_row(row)`

Convert A1 row string to 0-indexed number.

```js
XLSX.utils.decode_row("1");     // 0
XLSX.utils.decode_row("100");   // 99
```

### `decode_col(col)`

Convert A1 column string to 0-indexed number.

```js
XLSX.utils.decode_col("A");     // 0
XLSX.utils.decode_col("Z");     // 25
XLSX.utils.decode_col("AA");    // 26
XLSX.utils.decode_col("XFD");   // 16383
```

### `decode_range(range)`

Convert range string to `{ s: { r, c }, e: { r, c } }`.

```js
XLSX.utils.decode_range("A1:D10");
// { s: { r: 0, c: 0 }, e: { r: 9, c: 3 } }

XLSX.utils.decode_range("B2");
// Single cell lifted to range: { s: { r: 1, c: 1 }, e: { r: 1, c: 1 } }
```

## Iterating Over a Range

```js
const range = XLSX.utils.decode_range(ws["!ref"]);

for (let R = range.s.r; R <= range.e.r; ++R) {
  for (let C = range.s.c; C <= range.e.c; ++C) {
    const addr = XLSX.utils.encode_cell({ r: R, c: C });
    const cell = ws[addr];
    if (cell && cell.v !== undefined) {
      console.log(`${addr}: ${cell.v}`);
    }
  }
}
```

## Common Patterns

### Find the last used row

```js
const range = XLSX.utils.decode_range(ws["!ref"]);
const lastRow = range.e.r; // 0-indexed
```

### Find the next empty row

```js
let nextRow = 0;
if (ws["!ref"]) {
  const range = XLSX.utils.decode_range(ws["!ref"]);
  nextRow = range.e.r + 1;
}
```

### Convert between absolute and relative references

```js
// Absolute: $A$1, Relative: A1, Mixed: $A1 or A$1
// SheetJS always uses absolute references internally
```

### Check if a cell is within a range

```js
function isInRange(cell, range) {
  return cell.r >= range.s.r && cell.r <= range.e.r &&
         cell.c >= range.s.c && cell.c <= range.e.c;
}
```

### Get row/column count from range

```js
const range = XLSX.utils.decode_range("A1:D10");
const rowCount = range.e.r - range.s.r + 1;   // 10
const colCount = range.e.c - range.s.c + 1;   // 4
```

### Generate column letter from index (manual)

```js
function colToLetter(col) {
  let result = "";
  while (col >= 0) {
    result = String.fromCharCode((col % 26) + 65) + result;
    col = Math.floor(col / 26) - 1;
  }
  return result;
}
colToLetter(0);   // "A"
colToLetter(26);  // "AA"
```
