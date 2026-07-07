# Cell Addresses and Ranges

## Coordinate System

SheetJS uses 0-indexed coordinates (JavaScript convention), while Excel uses 1-indexed:

| Excel | SheetJS |
|---|---|
| Row 1 | Row 0 |
| Column A | Column 0 |
| Cell A1 | `{ r: 0, c: 0 }` |
| Cell C4 | `{ r: 3, c: 2 }` |

## Cell Addresses

### Encoding

```js
XLSX.utils.encode_cell({ r: 0, c: 0 });   // "A1"
XLSX.utils.encode_cell({ r: 3, c: 2 });   // "C4"
XLSX.utils.encode_col(0);                  // "A"
XLSX.utils.encode_col(25);                 // "Z"
XLSX.utils.encode_col(26);                 // "AA"
XLSX.utils.encode_row(0);                  // "1"
XLSX.utils.encode_row(10);                 // "11"
```

### Decoding

```js
XLSX.utils.decode_cell("A1");              // { r: 0, c: 0 }
XLSX.utils.decode_cell("C4");              // { r: 3, c: 2 }
XLSX.utils.decode_col("A");                // 0
XLSX.utils.decode_col("Z");                // 25
XLSX.utils.decode_col("AA");               // 26
XLSX.utils.decode_row("1");                // 0
XLSX.utils.decode_row("11");               // 10
```

## Ranges

### Encoding

```js
XLSX.utils.encode_range({ s: { r: 0, c: 0 }, e: { r: 9, c: 3 } }); // "A1:D10"
XLSX.utils.encode_range({ s: { r: 0, c: 0 }, e: { r: 0, c: 2 } }); // "A1:C1"
```

### Decoding

```js
XLSX.utils.decode_range("A1:D10");
// { s: { r: 0, c: 0 }, e: { r: 9, c: 3 } }

XLSX.utils.decode_range("A1");
// { s: { r: 0, c: 0 }, e: { r: 0, c: 0 } } — single cell as range
```

## Iterating Over a Worksheet

### Sparse Mode

```js
const range = XLSX.utils.decode_range(ws["!ref"]);
for (let R = range.s.r; R <= range.e.r; R++) {
  for (let C = range.s.c; C <= range.e.c; C++) {
    const addr = XLSX.utils.encode_cell({ r: R, c: C });
    const cell = ws[addr];
    if (cell) {
      console.log(addr, cell.v);
    }
  }
}
```

### Dense Mode

```js
const range = XLSX.utils.decode_range(ws["!ref"]);
for (let R = range.s.r; R <= range.e.r; R++) {
  for (let C = range.s.c; C <= range.e.c; C++) {
    const cell = ws["!data"]?.[R]?.[C];
    if (cell) {
      const addr = XLSX.utils.encode_cell({ r: R, c: C });
      console.log(addr, cell.v);
    }
  }
}
```

### Auto-Detect Mode

```js
const range = XLSX.utils.decode_range(ws["!ref"]);
const dense = ws["!data"] != null;
for (let R = range.s.r; R <= range.e.r; R++) {
  for (let C = range.s.c; C <= range.e.c; C++) {
    const cell = dense
      ? ws["!data"]?.[R]?.[C]
      : ws[XLSX.utils.encode_cell({ r: R, c: C })];
    if (cell) {
      // process cell
    }
  }
}
```

## Column Limits

| Limit | Value |
|---|---|
| Max columns | 16384 (XFD) |
| Max rows | 1048576 |
| Full column range | `{ s: { c: 0, r: 0 }, e: { c: 0, r: 1048575 } }` (A:A) |
| Full row range | `{ s: { c: 0, r: 0 }, e: { c: 16383, r: 0 } }` (1:1) |

## Helper Functions

### Check if address is in range

```js
function isInRange(addr, range) {
  const cell = XLSX.utils.decode_cell(addr);
  return (
    cell.r >= range.s.r && cell.r <= range.e.r &&
    cell.c >= range.s.c && cell.c <= range.e.c
  );
}
```

### Get row count

```js
const range = XLSX.utils.decode_range(ws["!ref"]);
const rowCount = range.e.r - range.s.r + 1;
```

### Get column count

```js
const range = XLSX.utils.decode_range(ws["!ref"]);
const colCount = range.e.c - range.s.c + 1;
```
