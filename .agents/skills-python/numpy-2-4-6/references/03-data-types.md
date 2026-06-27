# 03 — Data Types

## dtype System

Every NumPy array has a `dtype` (data type) that determines the size, byte order, and interpretation of each element.

### Scalar types

| Type | Name | Bits | Description |
|---|---|---|---|
| `np.bool` / `np.bool_` | `bool` | 8 | Boolean |
| `np.int8` / `np.byte` | `int8` | 8 | Signed integer |
| `np.uint8` / `np.ubyte` | `uint8` | 8 | Unsigned integer |
| `np.int16` / `np.short` | `int16` | 16 | Signed integer |
| `np.uint16` / `np.ushort` | `uint16` | 16 | Unsigned integer |
| `np.int32` / `np.intc` | `int32` | 32 | Signed integer |
| `np.uint32` / `np.uintc` | `uint32` | 32 | Unsigned integer |
| `np.int64` / `np.longlong` | `int64` | 64 | Signed integer |
| `np.uint64` / `np.ulonglong` | `uint64` | 64 | Unsigned integer |
| `np.intp` | `intp` | platform | Integer for indexing (size_t) |
| `np.float16` / `np.half` | `float16` | 16 | Half-precision float |
| `np.float32` / `np.single` | `float32` | 32 | Single-precision float |
| `np.float64` / `np.double` | `float64` | 64 | Double-precision float |
| `np.longdouble` | `longdouble` | platform | Extended-precision float |
| `np.complex64` / `np.csingle` | `complex64` | 64 | Complex (2× float32) |
| `np.complex128` / `np.cdouble` | `complex128` | 128 | Complex (2× float64) |
| `np.str_` | `str` | variable | Unicode string |
| `np.bytes_` | `bytes` | variable | Byte string |
| `np.object_` | `object` | pointer | Python object reference |
| `np.void` | `void` | variable | Raw bytes |

### Creating dtypes

```python
np.dtype('float64')              # from string
np.dtype(np.float32)             # from type
np.dtype('f8')                   # character code
np.dtype([('x', 'f4'), ('y', 'i4')])  # structured dtype
np.dtype('i8, f4, S3')           # comma-separated shorthand
```

### Character codes

Single-character codes: `?` (bool), `i` (signed int), `u` (unsigned int), `f` (float), `c` (complex), `m` (timedelta), `M` (datetime), `O` (object), `S`/`a` (bytes), `U` (unicode), `V` (void).

Prefix with byte order: `<` (little-endian), `>` (big-endian), `=` (native), `|` (not applicable).

Suffix with bit size: `i4` = int32, `f8` = float64, `U10` = unicode string of 10 characters.

### Type queries and conversions

```python
a.dtype                          # dtype of array
np.issubdtype(a.dtype, np.integer)   # is integer type?
np.issubdtype(a.dtype, np.floating)  # is floating point?
np.can_cast('int32', 'float64')      # can safely cast?
np.result_type(a, b)                 # result dtype of a op b
np.promote_types('int32', 'float64') # common promoted type
```

### Type hierarchy

```
generic
├── number
│   ├── integer
│   │   ├── signedinteger (int8, int16, int32, int64)
│   │   └── unsignedinteger (uint8, uint16, uint32, uint64)
│   ├── floating (float16, float32, float64, longdouble)
│   └── complexfloating (complex64, complex128)
├── character (bytes_, str_)
├── datetime (datetime64, timedelta64)
└── object_
```

## Type Promotion Rules

NumPy uses "type promotion" to determine output dtypes for operations:

```python
int32 + int32  → int32       # same type preserved
int32 + float64 → float64    # wider type wins
uint32 + int32  → int64      # signed/unsigned mix upcasts
int32 + complex128 → complex128
```

Use `np.result_type()` to check what dtype an operation will produce. Use the `dtype=` kwarg on ufuncs to override.

## Converting dtypes

```python
a.astype(np.float64)                      # always returns a copy
a.astype(np.float64, casting='safe')      # only safe casts allowed
a.astype(np.float64, casting='same_value')# value must not change (2.4+)
a.view(np.float32)                        # reinterpret bytes (no copy, same size required)
```

Casting modes:
- `'no'` — no casting at all
- `'equiv'` — only if dtype and byte order match
- `'safe'` — only if values are preserved exactly
- `'same_kind'` — only within kind (int→int, float→float)
- `'unsafe'` — any cast allowed
- `'same_value'` — value must not change (new in 2.4)

## Structured Arrays

Structured arrays store heterogeneous data with named fields, similar to C structs.

### Creating structured dtypes

```python
# Method 1: list of tuples
dt = np.dtype([('name', 'U10'), ('age', 'i4'), ('weight', 'f4')])

# Method 2: comma-separated string
dt = np.dtype('U10, i4, f4')

# Method 3: dictionary
dt = np.dtype({
    'names': ['x', 'y'],
    'formats': ['f4', 'f4'],
    'offsets': [0, 4],
    'itemsize': 8
})

# Method 4: aligned struct
dt = np.dtype([('a', 'i4'), ('b', 'f8')], align=True)
```

### Creating structured arrays

```python
arr = np.array([('Rex', 9, 81.0), ('Fido', 3, 27.0)], dtype=dt)
arr['name']       # array of names: ['Rex', 'Fido']
arr['age']        # array of ages: [9, 3]
arr[0]['weight']  # single element field access
```

### Accessing fields

```python
arr['age']              # view of age column
arr[['name', 'age']]    # subset of fields (new dtype)
arr.dtype.names          # ('name', 'age', 'weight')
arr.dtype.fields         # dict with (dtype, offset) per field
arr.dtype['age']         # dtype('int32')
```

### Nested structures

```python
dt = np.dtype([
    ('point', [('x', 'f4'), ('y', 'f4')]),
    ('color', 'u1', 3)          # subarray: 3 bytes
])
arr = np.zeros(5, dtype=dt)
arr['point']['x']              # access nested field
```

### When to use structured arrays

- **Good for**: C struct interop, binary buffer interpretation, fixed-format records
- **Not ideal for**: tabular data analysis — use pandas or xarray instead (better cache behavior, higher-level API)

## Record arrays (np.rec)

```python
rec = np.rec.array([('Rex', 9, 81.0)], dtype=dt)
rec.name    # attribute-style access (instead of rec['name'])
rec.age
```

Record arrays provide attribute access to fields but are a thin wrapper. Structured arrays with bracket notation are preferred for new code.

## Datetime and timedelta

```python
np.datetime64('2024-01-15')
np.datetime64('2024-01-15', 'D')     # explicit unit
np.datetime64('now')                 # current time
np.timedelta64(5, 'D')               # 5 days

# Arithmetic
dates = np.array(['2024-01-01', '2024-01-15', '2024-02-01'], dtype='datetime64[D]')
diff = dates - dates[0]              # timedelta64 array
```

Datetime units: `Y` (year), `M` (month), `W` (week), `D` (day), `h` (hour), `m` (minute), `s` (second), `ms` (millisecond), `us` (microsecond), `ns` (nanosecond).

Business day functions:

```python
np.is_busday('2024-01-15')           # is it a business day?
np.busday_offset('2024-01-15', 5)    # 5 business days from date
np.busday_count(start, stop)         # count business days in range
```
