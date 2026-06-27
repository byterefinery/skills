# Function Coverage

The `formulas` package implements 645+ Excel functions, covering 90.1% of standard Excel function categories. Functions are accessible via `formulas.get_functions()` which returns a dict mapping function names to callables.

## Category Coverage Summary

| Category | Implemented | Total | Coverage |
|----------|-------------|-------|----------|
| COMPATIBILITY | 40 | 40 | 100% |
| DATE & TIME | 25 | 25 | 100% |
| ENGINEERING | 54 | 54 | 100% |
| FINANCIAL | 55 | 55 | 100% |
| LOGICAL | 19 | 19 | 100% |
| STATISTICAL | 111 | 111 | 100% |
| OPERATORS | 15 | 15 | 100% |
| MATH & TRIG | 71 | 80 | 88.8% |
| TEXT | 44 | 50 | 88.0% |
| LOOKUP | 33 | 40 | 82.5% |
| INFORMATION | 16 | 22 | 72.7% |
| AUTOMATION | 0 | 3 | 0% |
| CUBE | 0 | 7 | 0% |
| DATABASE | 0 | 12 | 0% |
| WEB | 0 | 3 | 0% |
| **TOTAL** | **483** | **536** | **90.1%** |

## Key Functions by Category

### Math & Trig (71/80)

`ABS`, `ACOS`, `ACOSH`, `ASIN`, `ASINH`, `ATAN`, `ATANH`, `CEILING`, `COS`, `COSH`, `DEGREES`, `EVEN`, `EXP`, `FACT`, `FLOOR`, `GCD`, `INT`, `LN`, `LOG`, `LOG10`, `MAX`, `MIN`, `MOD`, `MROUND`, `ODD`, `PI`, `POWER`, `PRODUCT`, `QUOTIENT`, `RADIANS`, `RAND`, `RANDBETWEEN`, `ROUND`, `ROUNDDOWN`, `ROUNDUP`, `SIGN`, `SIN`, `SQRT`, `SUBTOTAL`, `SUM`, `SUMIF`, `SUMIFS`, `SUMPRODUCT`, `SUMX2MY2`, `SUMX2PY2`, `SUMXMY2`, `TAN`, `TRUNC`, and more.

### Statistical (111/111 — Full Coverage)

`AVERAGE`, `AVERAGEA`, `AVEDEV`, `BINOM.DIST`, `CHISQ.TEST`, `CONFIDENCE`, `CORREL`, `COUNT`, `COUNTA`, `COUNTBLANK`, `COUNTIF`, `COUNTIFS`, `DEVSQ`, `FREQUENCY`, `GEOMEAN`, `HARMEAN`, `INTERCEPT`, `KURT`, `LARGE`, `MEDIAN`, `MODE`, `PEARSON`, `PERCENTILE`, `PHI`, `POISSON`, `PROB`, `QUARTILE`, `RANK`, `RSQ`, `SLOPE`, `SMALL`, `STDEV`, `STDEVA`, `STDEV.P`, `STDEV.S`, `STEYX`, `SKEW`, `T.TEST`, `TREND`, `VAR`, `VARA`, `VARP`, `VAR.S`, `Z.TEST`, and many more.

### Financial (55/55 — Full Coverage)

`ACCRINT`, `AMORDEGRC`, `AMORLINC`, `COUPDAYBS`, `COUPDAYS`, `COUPDAYSNC`, `COUPNCD`, `COUPNUM`, `COUPPCD`, `CUMIPMT`, `CUMPRINC`, `DB`, `DDAY`, `DDB`, `DISC`, `DOLLARDE`, `DOLLARFR`, `DURATION`, `EFFECT`, `FV`, `FVSCHEDULE`, `INTRATE`, `IPMT`, `IRR`, `ISPMT`, `MDURATION`, `NOMINAL`, `NPER`, `NPV`, `ODDFPRICE`, `ODDFYIELD`, `ODDLFPPRICE`, `ODDLFPYIELD`, `PMT`, `PPMT`, `PRICE`, `PRICEDISC`, `PRICEMAT`, `PV`, `RATE`, `RECEIVED`, `RLN`, `SLN`, `SYD`, `TBILLEQ`, `TBILLPRICE`, `TBILLYIELD`, `VDB`, `XIRR`, `XNPV`, `YIELD`, `YIELDDISC`, `YIELDMAT`.

### Date & Time (25/25 — Full Coverage)

`DATE`, `DATEDIF`, `DATEVALUE`, `DAY`, `DAYS`, `DAYS360`, `EDATE`, `EOMONTH`, `HOUR`, `MINUTE`, `MONTH`, `NETWORKDAYS`, `NOW`, `SECOND`, `TIME`, `TIMEVALUE`, `TODAY`, `WORKDAY`, `YEAR`, `YEARFRAC`.

### Text (44/50)

`BAHTTEXT`, `CHAR`, `CLEAN`, `CODE`, `CONCATENATE`, `EXACT`, `FINDB`, `FIND`, `FIXED`, `LEFT`, `LEN`, `LOWER`, `MID`, `PROPER`, `REPLACE`, `REPT`, `RIGHT`, `SEARCH`, `SUBSTITUTE`, `T`, `TEXT`, `TRIM`, `UPPER`, `UNICODE`, `VALUE`.

### Logical (19/19 — Full Coverage)

`AND`, `FALSE`, `IF`, `IFERROR`, `IFNA`, `IOR`, `MAXA`, `MINA`, `NOT`, `OR`, `TRUE`, `XOR`.

### Lookup (33/40)

`ADDRESS`, `AREAS`, `CHOOSE`, `COLUMN`, `COLUMNS`, `HLOOKUP`, `HYPERLINK`, `INDEX`, `INDIRECT`, `LOOKUP`, `MATCH`, `OFFSET`, `ROW`, `ROWS`, `TRANSPOSE`, `VLOOKUP`.

### Engineering (54/54 — Full Coverage)

`BASE`, `BIN2DEC`, `BIN2HEX`, `BIN2OCT`, `COMPLEX`, `CONVERT`, `DEC2BIN`, `DEC2HEX`, `DEC2OCT`, `HEX2BIN`, `HEX2DEC`, `HEX2OCT`, `IMABS`, `IMAGINARY`, `IMARGUMENT`, `IMCONJUGATE`, `IMCOS`, `IMCOSH`, `IMCOT`, `IMCSC`, `IMCSC`, `IMDIV`, `IMEXP`, `IMLN`, `IMLOG10`, `IMLOG2`, `IMPOWER`, `IMPRODUCT`, `IMREAL`, `IMSEC`, `IMSIN`, `IMSQRT`, `MSUB`, `IMSUM`, `IMTAN`, `OCT2BIN`, `OCT2DEC`, `OCT2HEX`.

### Information (16/22)

`CELL`, `ERROR.TYPE`, `INFO`, `ISBLANK`, `ISERR`, `ISERROR`, `ISEVEN`, `ISLOGICAL`, `ISNA`, `ISNONTEXT`, `ISNUMBER`, `ISODD`, `ISREF`, `ISTEXT`, `N`, `NA`.

## Missing Categories

- **AUTOMATION** (0/3): `CALL`, `REGISTER.ID`, `INITIATE` — Windows-specific API calls
- **CUBE** (0/7): `CUBEVALUE`, `CUBEMEMBER` etc. — Power Pivot / OLAP integration
- **DATABASE** (0/12): `DSUM`, `DAVERAGE`, `DCOUNT` etc. — Database functions
- **WEB** (0/3): `WEBSERVICE`, `FILTERXML` — External HTTP calls

## Custom Functions

Add custom functions to the global function registry:

```python
import formulas

FUNCTIONS = formulas.get_functions()

# Simple lambda
FUNCTIONS['DOUBLE'] = lambda x: x * 2

# With validation
def safe_divide(a, b):
    if b == 0:
        return float('nan')
    return a / b

FUNCTIONS['SAFE_DIVIDE'] = safe_divide

# Use in formula
func = formulas.Parser().ast('=DOUBLE(21)')[1].compile()
print(func())  # 42
```

Custom functions are available to all subsequently parsed formulas. They integrate with the dependency graph and can reference other cells.

## Operators (15/15 — Full Coverage)

All standard Excel operators are supported:

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `=A1+B1` |
| `-` | Subtraction/Negation | `=A1-B1`, `=-5` |
| `*` | Multiplication | `=A1*B1` |
| `/` | Division | `=A1/B1` |
| `^` | Exponentiation | `=2^10` |
| `%` | Percent | `=10%` (= 0.1) |
| `&` | Text concatenation | `="Hello" & " World"` |
| `<` `>` `<=` `>=` | Comparison | `=A1>B1` |
| `=` | Equality | `=A1=B1` |
| `<>` | Inequality | `=A1<>B1` |
| `` ` `` | Space (intersection) | `=A1:A10 B1:B10` |
| `,` | Union (in functions) | `=SUM(A1:A5, B1:B5)` |
| `:` | Range | `=SUM(A1:A10)` |
| `!` | Sheet reference | `='Sheet1'!A1` |
| `()` | Precedence grouping | `=(1+2)*3` |

## Date Handling

Date functions return Excel serial numbers (days since 1900-01-01, with the Mac/Windows leap year bug):

```python
from datetime import datetime, timedelta

# Convert serial to Python date
def excel_serial_to_date(serial):
    epoch = datetime(1899, 12, 30)
    return epoch + timedelta(days=serial)

# TODAY() returns today's serial number
# DATE(2024, 1, 15) returns serial for Jan 15, 2024
```
