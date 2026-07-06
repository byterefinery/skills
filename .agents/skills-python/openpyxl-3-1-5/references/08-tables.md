# Tables

## Table Object

Excel tables with structured references, auto-filters, and formatting.

```python
from openpyxl.worksheet.table import Table, TableStyleInfo

# Create a table
table = Table(displayName="SalesTable", ref="A1:D10")

# Add style
table.tableStyleInfo = TableStyleInfo(
    name="TableStyleMedium9",
    showFirstColumn=False,
    showLastColumn=False,
    showRowStripes=True,
    showColumnStripes=False
)

# Add to worksheet
ws.add_table(table)
```

## Table Style Info

```python
from openpyxl.worksheet.table import TableStyleInfo

# Available style families:
# TableStyleMedium1-28, TableStyleLight1-21, TableStyleDark1-11

style = TableStyleInfo(
    name="TableStyleMedium9",
    showFirstColumn=True,    # Bold first column
    showLastColumn=True,     # Bold last column
    showRowStripes=True,     # Banded rows
    showColumnStripes=False  # Banded columns
)
```

## Table Columns

```python
from openpyxl.worksheet.table import Table, TableColumn

# Create table with named columns
table = Table(displayName="MyTable", ref="A1:C10")

# Add columns (auto-generated from range if not specified)
table.tableColumns = [
    TableColumn(id=1, name="Name"),
    TableColumn(id=2, name="Score"),
    TableColumn(id=3, name="Grade"),
]

# Column properties
col = TableColumn(id=1, name="Total")
col.totalsRowFunction = "sum"    # "sum", "min", "max", "average",
                                  # "count", "countNums", "stdDev", "var", "custom"
col.totalsRowLabel = "Total"     # Custom label for totals row
col.headerRowCellStyle = "Header"  # Named style for header
col.dataCellStyle = "Data"        # Named style for data cells

# Add to table
table.tableColumns.append(col)
```

## Calculated Columns

```python
from openpyxl.worksheet.table import Table, TableColumn, TableFormula

# Calculated column with formula
col = TableColumn(id=3, name="Total")
col.calculatedColumnFormula = TableFormula(attr_text="=[@Price]*[@Qty]")
table.tableColumns.append(col)

# Array formula
col.calculatedColumnFormula = TableFormula(array=True, attr_text="=SUM([@Scores])")
```

## Totals Row

```python
# Show totals row
table.totalsRowShown = True

# Set aggregation function per column
table.tableColumns[0].totalsRowFunction = "sum"
table.tableColumns[1].totalsRowFunction = "average"
table.tableColumns[2].totalsRowFunction = "count"
```

## Auto-Filter on Tables

```python
from openpyxl.worksheet.filters import AutoFilter

# Auto-filter is enabled by default when headerRowCount > 0
table.autoFilter = AutoFilter(ref="A1:D10")

# Add column filter
table.autoFilter.add_filter_column(col_id=0, vals=["Alice", "Bob"])

# Add sort condition
table.autoFilter.add_sort_condition("A2:A10", descending=False)
```

## Table Properties

```python
table.id = 1                        # Table ID
table.displayName = "SalesTable"    # Display name (no spaces allowed)
table.name = "SalesTable"           # Internal name
table.comment = "Monthly sales"     # Table comment
table.ref = "A1:D10"                # Cell range
table.tableType = "worksheet"       # "worksheet", "xml", "queryTable"
table.headerRowCount = 1            # Number of header rows
table.insertRow = None              # Allow insert row animation
table.insertRowShift = None         # Shift on insert
table.totalsRowCount = None         # Number of totals rows
table.totalsRowShown = False        # Show totals row
table.published = None              # Published table
```

## Accessing Tables

```python
# Get tables on a worksheet
for name, ref in ws.tables.items():
    print(f"Table: {name}, Range: {ref}")

# Get specific table
table = ws.tables.get("SalesTable")
table = ws.tables.get(table_range="A1:D10")

# Column names
print(table.column_names)  # ['Name', 'Score', 'Grade']
```

## Complete Example

```python
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo, TableColumn

wb = Workbook()
ws = wb.active

# Write data
ws.append(["Name", "Dept", "Salary", "Bonus"])
ws.append(["Alice", "Engineering", 85000, 5000])
ws.append(["Bob", "Sales", 72000, 8000])
ws.append(["Charlie", "Engineering", 90000, 6000])
ws.append(["Diana", "Marketing", 68000, 4000])

# Create table
table = Table(displayName="EmployeeTable", ref="A1:D5")

# Style
table.tableStyleInfo = TableStyleInfo(
    name="TableStyleMedium9",
    showFirstColumn=False,
    showLastColumn=False,
    showRowStripes=True,
    showColumnStripes=False
)

# Show totals
table.totalsRowShown = True
for col in table.tableColumns:
    if col.name in ("Salary", "Bonus"):
        col.totalsRowFunction = "sum"

ws.add_table(table)

wb.save("employees.xlsx")
```
