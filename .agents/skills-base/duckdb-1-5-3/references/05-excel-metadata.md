# Excel Metadata — Sheet Discovery, Cell Types, and Formula Handling

DuckDB's Excel extension reads XLSX files as tabular data but does not provide a dedicated metadata introspection function. This reference covers workarounds for sheet discovery, understanding cell types, and how formula cells are handled.

## Understanding XLSX Structure

An `.xlsx` file is a ZIP archive containing XML parts:

```
report.xlsx (ZIP archive)
├── [Content_Types].xml          # File type declarations
├── _rels/.rels                  # Package relationships
├── xl/
│   ├── workbook.xml             # Sheet names, order, visibility
│   ├── styles.xml               # Cell formatting definitions
│   ├── sharedStrings.xml        # Deduplicated string values
│   ├── _rels/
│   │   └── workbook.xml.rels    # Sheet → worksheet mapping
│   └── worksheets/
│       ├── sheet1.xml           # Actual cell data for Sheet 1
│       └── sheet2.xml           # Actual cell data for Sheet 2
```

## Sheet Discovery

### Method 1: Error Message Suggestions (DuckDB-only)

Pass a non-existent sheet name to trigger suggestions in the error message:

```sql
SELECT * FROM read_xlsx('file.xlsx', sheet 'zzz_nonexistent') LIMIT 0;
-- Binder Error: Sheet "zzz_nonexistent" not found
-- Did you mean: "Sheet1", "Sales Data", "Summary"
```

Limitation: only shows a few suggestions, may not list all sheets if there are many.

### Method 2: Python zipfile + XML Parsing (recommended)

XLSX files are ZIP archives; parse `xl/workbook.xml` to extract sheet metadata:

```python
import zipfile
import xml.etree.ElementTree as ET

def list_xlsx_sheets(filepath):
    """Return list of sheet names from an XLSX file."""
    with zipfile.ZipFile(filepath) as z:
        tree = ET.parse(z.open('xl/workbook.xml'))
        root = tree.getroot()
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        sheets = root.find('.//main:sheets', ns)
        return [
            {
                'name': sheet.get('name'),
                'state': sheet.get('state', 'visible'),  # visible/hidden/veryHidden
                'id': sheet.get('sheetId')
            }
            for sheet in sheets.findall('main:sheet', ns)
        ]

sheets = list_xlsx_sheets('report.xlsx')
for s in sheets:
    print(f"Sheet: {s['name']}, State: {s['state']}, ID: {s['id']}")
```

### Method 3: Python zipfile — Sheet Count and Names

```python
import zipfile, xml.etree.ElementTree as ET

with zipfile.ZipFile('file.xlsx') as z:
    tree = ET.parse(z.open('xl/workbook.xml'))
    root = tree.getroot()
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    sheets = root.find('.//main:sheets', ns)
    sheet_elements = sheets.findall('main:sheet', ns)

    print(f"Number of sheets: {len(sheet_elements)}")
    for s in sheet_elements:
        print(f"  - {s.get('name')} (state: {s.get('state', 'visible')})")
```

## Getting Headers and Row Count

### Via DESCRIBE (DuckDB)

```sql
-- Get column names and types
DESCRIBE FROM read_xlsx('file.xlsx', header true);
```

Returns a table with columns: `column_name`, `column_type`, `null`, `column_default`, etc.

### Row Count

```sql
-- Count rows (reads entire sheet)
SELECT count(*) FROM read_xlsx('file.xlsx', header true);

-- Count without reading all data (estimate from file structure)
-- Not directly supported; must scan or use Python
```

### Via Python — Full Metadata Extraction

```python
import zipfile
import xml.etree.ElementTree as ET

def get_xlsx_metadata(filepath, sheet_name=None):
    """Extract comprehensive metadata from an XLSX file."""
    with zipfile.ZipFile(filepath) as z:
        # Get sheet names and resolve to worksheet path
        tree = ET.parse(z.open('xl/workbook.xml'))
        root = tree.getroot()
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        sheets_elem = root.find('.//main:sheets', ns)
        all_sheets = [s.get('name') for s in sheets_elem.findall('main:sheet', ns)]

        # Resolve sheet to worksheet XML path
        rels_tree = ET.parse(z.open('xl/_rels/workbook.xml.rels'))
        rels_root = rels_tree.getroot()
        rels_ns = {'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

        # Find target sheet
        target = sheet_name or all_sheets[0]
        sheet_elem = None
        for s in sheets_elem.findall('main:sheet', ns):
            if s.get('name') == target:
                sheet_elem = s
                break

        if not sheet_elem:
            return {'error': f'Sheet "{target}" not found. Available: {all_sheets}'}

        # Resolve r:id to worksheet path
        rid = sheet_elem.get('r:id')
        rel_target = None
        for rel in rels_root.findall('.//r:Relationship', rels_ns):
            if rel.get('Id') == rid:
                rel_target = rel.get('Target')
                break

        worksheet_path = f'xl/{rel_target}' if not rel_target.startswith('/') else rel_target.lstrip('/')

        # Parse worksheet to get dimensions
        ws_tree = ET.parse(z.open(worksheet_path))
        ws_root = ws_tree.getroot()
        dim_elem = ws_root.find('.//main:dimension', ns)
        dimension = dim_elem.get('ref') if dim_elem is not None else None

        # Count rows and columns from sheetData
        sheet_data = ws_root.find('.//main:sheetData', ns)
        row_count = 0
        max_col = 0
        if sheet_data is not None:
            for row in sheet_data.findall('main:row', ns):
                row_count += 1
                cols = row.findall('main:c', ns)
                if cols:
                    max_col = max(max_col, len(cols))

        # Get headers (first row values)
        headers = []
        if sheet_data is not None:
            first_row = sheet_data.find('main:row', ns)
            if first_row is not None:
                for cell in first_row.findall('main:c', ns):
                    v = cell.find('main:v', ns)
                    if v is not None:
                        headers.append(v.text)

        return {
            'file': filepath,
            'all_sheets': all_sheets,
            'sheet_name': target,
            'dimension': dimension,
            'row_count': row_count,
            'column_count': max_col,
            'headers': headers[:10],  # First 10 header values
        }

# Usage
meta = get_xlsx_metadata('report.xlsx')
for key, value in meta.items():
    print(f"{key}: {value}")
```

## Excel Cell Types

DuckDB recognizes these XLSX cell types internally:

| Cell Type | XML Attribute | DuckDB Type | Notes |
|-----------|--------------|-------------|-------|
| `NUMBER` | `t="n"` or no type | DOUBLE / DATE / TIME / TIMESTAMP | Depends on cell style format |
| `SHARED_STRING` | `t="s"` | VARCHAR | Value is index into shared strings table |
| `INLINE_STRING` | `t="inlineStr"` | VARCHAR | String stored directly in cell |
| `BOOLEAN` | `t="b"` | BOOLEAN | Stored as 0 or 1 in XML |
| `DATE` | `t="d"` | DATE | ISO 8601 date string |
| `ERROR` | `t="e"` | VARCHAR | Error code (e.g., `#DIV/0!`) |
| `FORMULA_STRING` | `t="str"` | VARCHAR | Result of a formula, stored as string |

### How Number Cells Become Dates/Times

A NUMBER cell's DuckDB type depends on its **style index** mapped through `xl/styles.xml`:

1. Cell has `s="5"` (style index 5)
2. `styles.xml` maps index 5 to a number format ID
3. Format ID maps to a format code like `mm/dd/yyyy` or `yyyy-mm-dd hh:mm:ss`
4. DuckDB infers: date format → DATE, time format → TIME, datetime → TIMESTAMP

If no style or unrecognized format, NUMBER cells default to DOUBLE.

## Formula Cell Handling

### How Formulas Are Read

DuckDB **does not evaluate Excel formulas**. It reads the pre-computed result values that Excel stored in the file:

```xml
<!-- In the XLSX XML -->
<c r="A3">
    <f>=SUM(A1:A2)</f>        <!-- The formula expression -->
    <v>42</v>                  <!-- The computed result -->
</c>
<c r="B3">
    <f>=VLOOKUP(B1,Data!A:D,2,FALSE)</f>
    <v>12345</v>
</c>
```

DuckDB reads `<v>` (the value), not `<f>` (the formula). If a cell has only a formula with no cached result, the behavior depends on how the file was saved:
- **FORMULA_STRING** (`t="str"`) — Formula result stored as string → read as VARCHAR
- **NUMBER with formula** — Numeric result → read as DOUBLE (or DATE/TIME based on style)

### No Formula Evaluation Engine

DuckDB has no Excel formula evaluation engine. Functions like `SUM`, `VLOOKUP`, `IF`, `XLOOKUP`, etc. are not interpreted. Only the stored result values are accessible.

To evaluate Excel formulas:
- Use a spreadsheet application (Excel, LibreOffice)
- Use Python libraries: `openpyxl` (reads formula expressions but doesn't evaluate), `xlwings` (connects to live Excel for evaluation)
- Recreate the logic in SQL using DuckDB's own functions

### Formula Cell Workaround — Reading Raw XML

If you need to inspect formula expressions themselves, parse the worksheet XML directly:

```python
import zipfile
import xml.etree.ElementTree as ET

def extract_formulas(filepath, sheet_name=None):
    """Extract cell positions and their formulas from an XLSX file."""
    with zipfile.ZipFile(filepath) as z:
        # Resolve sheet path (simplified — see full metadata function above)
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        tree = ET.parse(z.open('xl/worksheets/sheet1.xml'))  # Adjust path
        root = tree.getroot()
        sheet_data = root.find('.//main:sheetData', ns)

        formulas = []
        if sheet_data is not None:
            for row in sheet_data.findall('main:row', ns):
                for cell in row.findall('main:c', ns):
                    cell_ref = cell.get('r')
                    formula = cell.find('main:f', ns)
                    if formula is not None:
                        value = cell.find('main:v', ns)
                        formulas.append({
                            'cell': cell_ref,
                            'formula': formula.text,
                            'cached_value': value.text if value is not None else None
                        })
        return formulas

formulas = extract_formulas('report.xlsx')
for f in formulas:
    print(f"{f['cell']}: {f['formula']} → {f['cached_value']}")
```

## Sheet Visibility States

Sheets in a workbook can have three visibility states:

| State | Description | Readable by DuckDB? |
|-------|-------------|-------------------|
| `visible` (default) | Normal sheet | Yes |
| `hidden` | Hidden via UI (right-click → Hide) | Yes |
| `veryHidden` | Hidden programmatically, not visible in UI | Yes |

DuckDB can read all three states. The state is stored in `xl/workbook.xml`:
```xml
<sheet name="HiddenSheet" sheetId="2" state="hidden" r:id="rId2"/>
```

## File-Level Metadata

XLSX files store additional metadata in:
- `docProps/app.xml` — Application info, number of sheets/pages
- `docProps/core.xml` — Title, subject, author, created/modified dates
- `docProps/custom.xml` — Custom properties

```python
import zipfile
import xml.etree.ElementTree as ET

def get_xlsx_properties(filepath):
    """Extract document properties from an XLSX file."""
    with zipfile.ZipFile(filepath) as z:
        props = {}

        # Core properties
        try:
            tree = ET.parse(z.open('docProps/core.xml'))
            root = tree.getroot()
            dc_ns = {'dc': 'http://purl.org/dc/elements/1.1/',
                     'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'}
            props['title'] = root.find('dc:title', dc_ns).text if root.find('dc:title', dc_ns) is not None else None
            props['creator'] = root.find('dc:creator', dc_ns).text if root.find('dc:creator', dc_ns) is not None else None
            props['created'] = root.find('cp:created', dc_ns).text if root.find('cp:created', dc_ns) is not None else None
            props['modified'] = root.find('cp:modified', dc_ns).text if root.find('cp:modified', dc_ns) is not None else None
        except Exception:
            pass

        # App properties
        try:
            tree = ET.parse(z.open('docProps/app.xml'))
            root = tree.getroot()
            props['application'] = root.find('Application').text if root.find('Application') is not None else None
            props['sheets'] = root.find('Worksheets').text if root.find('Worksheets') is not None else None
        except Exception:
            pass

        return props

props = get_xlsx_properties('report.xlsx')
for k, v in props.items():
    print(f"{k}: {v}")
```
