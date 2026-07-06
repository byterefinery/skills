# Data Validation

## DataValidation Object

```python
from openpyxl.worksheet.datavalidation import DataValidation

# Create validation
dv = DataValidation(
    type="whole",              # Validation type
    operator="between",        # Comparison operator
    formula1="1",              # First formula/value
    formula2="100",            # Second formula/value (for between/notBetween)
    allow_blank=True,          # Allow empty cells
    showDropDown=False,        # Show drop-down (for list type)
    showErrorMessage=True,     # Show error on invalid input
    showInputMessage=True,     # Show prompt on cell selection
    errorStyle="stop",         # "stop", "warning", "information"
    errorTitle="Invalid Entry",
    error="Please enter a number between 1 and 100",
    promptTitle="Enter Value",
    prompt="Enter a number between 1 and 100",
    imeMode="noControl"        # IME mode for CJK input
)

# Apply to cells
dv.sqref = "A1:A10"           # Cell range
dv.add("B5")                   # Add individual cell

# Add to worksheet
ws.add_data_validation(dv)
```

## Validation Types

### Whole Numbers

```python
dv = DataValidation(type="whole", operator="between", formula1="1", formula2="100")
dv.sqref = "A1:A10"
ws.add_data_validation(dv)
```

### Decimal Numbers

```python
dv = DataValidation(type="decimal", operator="greaterThan", formula1="0")
dv.sqref = "B1:B10"
ws.add_data_validation(dv)
```

### Date

```python
dv = DataValidation(type="date", operator="between",
                    formula1="DATE(2024,1,1)", formula2="DATE(2024,12,31)")
dv.sqref = "C1:C10"
ws.add_data_validation(dv)
```

### Time

```python
dv = DataValidation(type="time", operator="between",
                    formula1="TIME(8,0,0)", formula2="TIME(18,0,0)")
dv.sqref = "D1:D10"
ws.add_data_validation(dv)
```

### Text Length

```python
dv = DataValidation(type="textLength", operator="lessThanOrEqual", formula1="50")
dv.sqref = "E1:E10"
ws.add_data_validation(dv)
```

### Drop-Down List

```python
# Inline list
dv = DataValidation(type="list", formula1='"Option1,Option2,Option3"', allow_blank=True)
dv.sqref = "F1:F10"
ws.add_data_validation(dv)

# List from cells
dv = DataValidation(type="list", formula1="=$Z$1:$Z$5", allow_blank=True)
dv.sqref = "F1:F10"
ws.add_data_validation(dv)

# List from another sheet
dv = DataValidation(type="list", formula1="'Lookup'!$A$1:$A$10")
dv.sqref = "F1:F10"
ws.add_data_validation(dv)
```

### Custom Formula

```python
# Custom validation using a formula
dv = DataValidation(type="custom", formula1="=AND(A1>0,A1<100)")
dv.sqref = "A1:A10"
ws.add_data_validation(dv)
```

## Operators

```python
# Available operators:
# "between", "notBetween", "equal", "notEqual",
# "lessThan", "lessThanOrEqual", "greaterThan", "greaterThanOrEqual"

# For "between" and "notBetween", use formula1 and formula2
dv = DataValidation(type="whole", operator="between", formula1="10", formula2="20")

# For single-value operators, use formula1 only
dv = DataValidation(type="whole", operator="greaterThan", formula1="0")
```

## Error and Prompt Messages

```python
dv = DataValidation(type="whole", operator="between", formula1="1", formula2="100")

# Error message (shown on invalid input)
dv.error = "Value must be between 1 and 100"
dv.errorTitle = "Invalid Value"
dv.errorStyle = "stop"        # "stop" (block), "warning" (allow with warning),
                              # "information" (show info, allow input)
dv.showErrorMessage = True

# Input prompt (shown when cell is selected)
dv.prompt = "Enter a whole number between 1 and 100"
dv.promptTitle = "Enter Value"
dv.showInputMessage = True
```

## Managing Validations

```python
# Access all validations
for dv in ws.data_validations.dataValidation:
    print(dv.sqref, dv.type, dv.formula1)

# Check if cell has validation
if "A5" in dv:
    print("A5 has validation")

# Add cell to existing validation
dv.add("A11")
dv.add("A12")
# sqref is updated: "A1:A10 A11 A12"

# Validation list properties
print(ws.data_validations.count)  # Number of validations
print(ws.data_validations.disablePrompts)  # Disable all prompts
```

## Common Patterns

```python
# Yes/No dropdown
dv = DataValidation(type="list", formula1='"Yes,No,Maybe"', allow_blank=True)
dv.sqref = "A1:A20"
ws.add_data_validation(dv)

# Priority dropdown
dv = DataValidation(type="list", formula1='"Low,Medium,High,Critical"')
dv.sqref = "B1:B20"
ws.add_data_validation(dv)

# Status dropdown
dv = DataValidation(type="list", formula1='"Not Started,In Progress,Completed,On Hold"')
dv.sqref = "C1:C20"
ws.add_data_validation(dv)

# Percentage (0-100)
dv = DataValidation(type="whole", operator="between", formula1="0", formula2="100")
dv.sqref = "D1:D20"
ws.add_data_validation(dv)

# Future date only
dv = DataValidation(type="date", operator="greaterThan", formula1="TODAY()")
dv.sqref = "E1:E20"
ws.add_data_validation(dv)
```
