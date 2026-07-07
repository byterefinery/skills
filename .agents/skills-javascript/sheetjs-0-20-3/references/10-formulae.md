# Formulae

## Basic Formulae

### Creating Formulae

SheetJS formulae use A1-style notation without the leading `=`:

```js
const ws = XLSX.utils.aoa_to_sheet([
  [1],
  [2],
  [{ t: "n", v: 3, f: "A1+A2" }]  // A3 = A1 + A2
]);
```

Or set directly:

```js
ws["A1"] = { t: "n", v: 1 };
ws["A2"] = { t: "n", v: 2 };
ws["A3"] = { t: "n", v: 3, f: "A1+A2" };
ws["!ref"] = "A1:A3";
```

### Reading Formulae

```js
const wb = XLSX.read(data, { cellFormula: true });
const cell = ws["A1"];
console.log(cell.f);  // formula string
console.log(cell.v);  // computed value (if available)
```

Cells with formulae but no computed value will have `f` but no `v`. The spreadsheet application calculates the value on open.

## Array Formulae

### Single-Cell Array Formula

```js
XLSX.utils.sheet_set_array_formula(ws, "C1", "SUM(A1:A3*B1:B3)");

// Manual:
ws["C1"] = { t: "n", f: "SUM(A1:A3*B1:B3)", F: "C1:C1" };
```

### Multi-Cell Array Formula

```js
XLSX.utils.sheet_set_array_formula(ws, "D1:D3", "A1:A3*B1:B3");

// Manual:
ws["D1"] = { t: "n", f: "A1:A3*B1:B3", F: "D1:D3" };
ws["D2"] = { t: "n", F: "D1:D3" };
ws["D3"] = { t: "n", F: "D1:D3" };
```

Only the top-left cell stores the formula. All cells share the `F` range.

## Dynamic Array Formulae

Dynamic array formulae are supported in XLSX/XLSM and XLSB:

```js
XLSX.utils.sheet_set_array_formula(ws, "C1", "_xlfn.UNIQUE(A1:A10)", true);

// Manual:
ws["C1"] = { t: "s", f: "_xlfn.UNIQUE(A1:A10)", F: "C1", D: true };
```

The `D: true` property marks the formula as dynamic, allowing Excel to auto-expand the range.

## `_xlfn.` Prefix

Functions introduced in newer Excel versions require the `_xlfn.` prefix for compatibility:

```js
// These functions need _xlfn. prefix:
"_xlfn.UNIQUE()"
"_xlfn.FILTER()"
"_xlfn.XLOOKUP()"
"_xlfn.IFS()"
"_xlfn.SWITCH()"
"_xlfn.TEXTJOIN()"
"_xlfn.RANDARRAY()"
"_xlfn.SEQUENCE()"
"_xlfn.LAMBDA()"
"_xlfn.LET()"
"_xlfn.FORMULATEXT()"
"_xlfn.ISFORMULA()"
```

Full list of functions requiring the prefix includes: ACOT, ACOTH, AGGREGATE, ARABIC, BASE, BETA.DIST, BINOM.DIST, BITAND, BITLSHIFT, BITOR, BITRSHIFT, BITXOR, BYCOL, BYROW, CEILING.MATH, CEILING.PRECISE, CHISQ.DIST, COT, COTH, COVARIANCE.P, COVARIANCE.S, CSC, CSCH, DAYS, DECIMAL, ECMA.CEILING, ERF.PRECISE, ERFC.PRECISE, EXPON.DIST, F.DIST, FORECAST.ETS*, FORMULATEXT, GAMMA, GAMMA.DIST, GAMMALN.PRECISE, GAUSS, HYPGEOM.DIST, IFNA, IFS, IMCOSH, IMCOT, IMCSC, IMCSCH, IMSEC, IMSECH, IMSINH, IMTAN, ISFORMULA, ISO.CEILING, ISOMITTED, ISOWEEKNUM, LAMBDA, LET, LOGNORM.DIST, MAKEARRAY, MAP, MAXIFS, MINIFS, MODE.MULT, MODE.SNGL, MUNIT, NEGBINOM.DIST, NETWORKDAYS.INTL, NORM.DIST, NORM.INV, NUMBERVALUE, PDURATION, PERCENTILE.EXC, PERCENTILE.INC, PERCENTRANK.EXC, PERCENTRANK.INC, PERMUTATIONA, PHI, POISSON.DIST, QUARTILE.EXC, QUARTILE.INC, QUERYSTRING, RANDARRAY, RANK.AVG, RANK.EQ, REDUCE, RRI, SCAN, SEC, SECH, SEQUENCE, SHEET, SHEETS, SKEW.P, SORTBY, STDEV.P, STDEV.S, SWITCH, T.DIST, TEXTJOIN, UNICHAR, UNICODE, UNIQUE, VAR.P, VAR.S, WEBSERVICE, WEIBULL.DIST, WORKDAY.INTL, XLOOKUP, XOR, Z.TEST.

### Reading with Prefix Preservation

```js
const wb = XLSX.read(data, { xlfn: true });  // preserves _xlfn. prefixes
```

## Formula Localization

SheetJS always uses en-US function names and comma separators:

| Locale | Excel Formula | SheetJS Formula |
|---|---|---|
| en-US | `=COUNT(A1:C3)` | `COUNT(A1:C3)` |
| es-ES | `=CONTAR(A1:C3)` | `COUNT(A1:C3)` |
| de-DE | `=KLEINSTE(A1:A10;1)` | `SMALL(A1:A10,1)` |

SheetJS parsers normalize all formulae to en-US form. Writers output en-US form.

## Extracting Formulae

```js
const formulae = XLSX.utils.sheet_to_formulae(ws);
// ["A1=1", "B1=2", "C1=A1+B1", "D1:D3=A1:A3*B1:B3"]
```

Output format:
- Values: `A1=1`, `B1='text'`, `C1=TRUE`
- Formulae: `D1=A1+B1`
- Array formulae: `E1:E3=A1:A3*B1:B3`

## Caveats

- SheetJS CE does not evaluate formulae. The `.v` field holds the pre-computed value from the file.
- `EVALUATE` function is not valid in cell formulae in Excel (only in defined names).
- Circular references are not detected or resolved.
- Volatile functions (NOW, TODAY, RAND) are not recalculated.
- Cross-workbook references are preserved as-is.
