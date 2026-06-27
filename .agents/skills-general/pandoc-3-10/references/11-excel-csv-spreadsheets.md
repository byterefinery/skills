# Excel, CSV, and Spreadsheet Reference

Detailed reference for working with Excel spreadsheets (xlsx), CSV, and TSV files. These are **input-only formats** in pandoc — you can read them but cannot write to these formats.

## Excel (xlsx)

### Basic Conversions

```bash
# All sheets → Markdown (each sheet = ## heading + table)
pandoc -f xlsx -t markdown data.xlsx -o data.md

# All sheets → HTML (each sheet = <h2> + <table>)
pandoc -f xlsx -t html data.xlsx -o data.html

# All sheets → LaTeX
pandoc -f xlsx -t latex data.xlsx -o data.tex

# All sheets → plain text
pandoc -f xlsx -t plain data.xlsx

# All sheets → JSON AST (for programmatic extraction)
pandoc -f xlsx -t json data.xlsx | python3 -m json.tool
```

### Sheet Structure in Output

Each worksheet becomes a level-2 heading followed by a table:

```markdown
## Sales Data {#sheet-1}

  Product   Q1      Q2      Q3
  --------- ------- ------- -------
  Widget    100.0   150.0   200.0
  Gadget    80.0    120.0   160.0

## Inventory {#sheet-2}

  Item      Stock
  --------- -------
  Part A    5000.0
  Part B    3000.0
```

- Sheet name becomes the H2 heading text
- Auto-generated ID: `#sheet-N` where N is sheet index (1-based)
- First row of data becomes table headers (if any)
- Cell formatting (bold, italic) is preserved in markdown output
- Empty sheets produce a heading with an empty table

### Programmatic Data Extraction

Since pandoc cannot output CSV/TSV directly, use the JSON AST for programmatic extraction:

```bash
# Convert to JSON AST
pandoc -f xlsx -t json data.xlsx > data-ast.json

# Parse with Python
python3 << 'EOF'
import json

with open('data-ast.json') as f:
    ast = json.load(f)

# Navigate: blocks = [Header, Table, Header, Table, ...]
for block in ast['blocks']:
    if block['t'] == 'Header':
        # Sheet name from heading text
        name = ''.join(item.get('c', '') for item in block['c'][2] if item.get('t') == 'Str')
        print(f"Sheet: {name}")
    elif block['t'] == 'Table':
        # Table structure: c[3] = head, c[4] = body
        # Headers: c[3][1][row_idx][1] = cells
        # Body rows: c[4][group_idx][3][row_idx][1] = cells
        pass
EOF
```

### Complete Extraction Utility

For extracting xlsx data as CSV or JSON, use a Python script that parses pandoc's JSON AST:

```python
#!/usr/bin/env python3
"""Extract xlsx/CSV data as CSV or JSON using pandoc JSON AST."""
import json, csv, sys, subprocess

def inline_text(inlines):
    """Extract text preserving spaces from inline elements."""
    result = []
    for item in inlines:
        t = item.get('t', '')
        if t == 'Str':
            result.append(item.get('c', ''))
        elif t == 'Space':
            result.append(' ')
    return ''.join(result)

def cell_text(cell):
    """Extract text from a table cell."""
    try:
        container = cell[4][0]  # Plain inline block
        children = container.get('c', [])
        return inline_text(children)
    except (IndexError, TypeError):
        return ""

def extract_table(table_ast):
    """Extract headers and rows from Table AST node."""
    c = table_ast['c']
    headers = []
    if len(c) > 3 and len(c[3]) > 1:
        for row_wrapper in c[3][1]:
            if len(row_wrapper) > 1:
                headers = [cell_text(cell) for cell in row_wrapper[1]]
                if any(headers):
                    break
    rows = []
    if len(c) > 4 and c[4]:
        for group in c[4]:
            if len(group) > 3:
                for row_wrapper in group[3]:
                    if len(row_wrapper) > 1:
                        rows.append([cell_text(cell) for cell in row_wrapper[1]])
    return headers, rows

# Usage
result = subprocess.run(['pandoc', '-f', 'xlsx', '-t', 'json', 'data.xlsx'],
                       capture_output=True, text=True)
ast = json.loads(result.stdout)

sheets = {}
current_name = None
for block in ast['blocks']:
    if block['t'] == 'Header':
        current_name = inline_text(block['c'][2])
    elif block['t'] == 'Table':
        headers, rows = extract_table(block)
        name = current_name or 'Sheet 1'
        sheets[name] = {'headers': headers, 'rows': rows}

# Output as CSV
for name, data in sheets.items():
    print(f"# {name}")
    writer = csv.writer(sys.stdout)
    if data['headers']:
        writer.writerow(data['headers'])
    for row in data['rows']:
        writer.writerow(row)
    print()

# Or output as JSON
print(json.dumps(sheets, indent=2))
```

### Sheet Selection via Lua Filters

Pandoc has no built-in option to select individual sheets. Use a Lua filter:

```lua
-- select-sheet.lua: Keep only the named sheet
function Pandoc(doc)
  local target = doc.meta["sheet-name"] or ""
  local new_blocks = {}
  local current_sheet = nil

  for _, block in ipairs(doc.blocks) do
    if block.t == "Header" then
      current_sheet = pandoc.utils.stringify(block)
    end
    if current_sheet == target or target == "" then
      table.insert(new_blocks, block)
    end
  end

  return pandoc.Pandoc(new_blocks)
end
```

Usage: `pandoc -f xlsx --lua-filter=select-sheet.lua -M sheet-name="Sales" data.xlsx -t markdown`

## CSV Input

### Basic Conversions

```bash
# CSV → Markdown (simple table)
pandoc -f csv -t markdown data.csv

# CSV → HTML (full HTML table with thead/tbody)
pandoc -f csv -t html data.csv

# CSV → LaTeX (longtable)
pandoc -f csv -t latex data.csv

# CSV → JSON AST
pandoc -f csv -t json data.csv | python3 -m json.tool
```

### CSV Structure

CSV files produce a single table. The first row is treated as headers. No sheet concept — one file = one table.

```bash
# Example CSV
echo -e "Name,Age,City\nAlice,30,NYC\nBob,25,London" > data.csv

# → Markdown
pandoc -f csv -t markdown data.csv
```

Output:
```markdown
  Name   Age   City
  ------ ----- ------
  Alice  30    NYC
  Bob    25    London
```

## TSV Input

Identical to CSV but uses tabs as delimiters:

```bash
# TSV → Markdown
pandoc -f tsv -t markdown data.tsv

# TSV → HTML
pandoc -f tsv -t html data.tsv
```

## Format Comparison

| Feature | xlsx | csv | tsv |
|---|---|---|---|
| Input only | Yes | Yes | Yes |
| Output support | No | No | No |
| Multi-sheet | Yes (all converted) | No (single table) | No (single table) |
| Headers auto-detected | First data row | First row | First row |
| Cell formatting preserved | Bold/italic in md/html | No | No |
| Empty cells | Preserved as empty | Preserved | Preserved |
| Number formatting | As-is (e.g., `1.0e-3`) | As-is | As-is |

## Converting TO CSV/TSV

Since pandoc cannot output CSV/TSV, use these alternatives:

### From Markdown Tables

```bash
# Extract tables from markdown as CSV using the JSON AST
pandoc -t json document.md > doc-ast.json
python3 extract_tables.py doc-ast.json  # custom script
```

### From HTML Tables

```bash
# Convert HTML table to CSV via markdown intermediate
pandoc -f html -t markdown page.html | python3 parse-md-tables.py
```

### From Other Formats

```bash
# Any format → markdown → parse tables programmatically
pandoc -f docx -t markdown report.docx | python3 extract_tables.py

# Direct JSON AST approach (most flexible)
pandoc -f latex -t json paper.tex > ast.json
python3 extract_tables.py ast.json
```

## Gotchas

- **xlsx is input-only** — no `-t xlsx` output format exists. For spreadsheet-like output, use markdown tables or HTML tables.
- **All sheets are converted** — pandoc converts every sheet in an xlsx file. There is no `--sheet` option. Use Lua filters for selection.
- **xlsx path bug** — some tools (e.g., openpyxl) create files with absolute paths in workbook relationships (`/xl/worksheets/sheet1.xml` instead of `worksheet/sheet1.xml`). These fail with `Entry not found: xl//xl/worksheets/sheet1.xml`. Files from Excel/LibreOffice work correctly.
- **No CSV/TSV output** — pandoc cannot write CSV or TSV files. The JSON AST is the bridge for programmatic data extraction.
- **Numbers become strings** — all cell values are converted to text. `100` becomes `"100"`, `3.14` becomes `"3.14"`, scientific notation `1.0e-3` stays as-is.
- **Merged cells** — only the top-left cell gets the content; other merged positions are empty.
- **Formulas** — stored values are extracted, not formulas themselves.
