# Builtin Functions

## General

| Function | Description |
|----------|-------------|
| `length` | Length of string/array/object, absolute value of number, 0 for null |
| `utf8bytelength` | Byte length of string in UTF-8 |
| `keys` | Sorted keys of object, or valid indices of array |
| `keys_unsorted` | Keys in insertion order (roughly) |
| `has(key)` | Whether object has key or array has index |
| `in(obj)` | Inverse of `has` — whether input is a key/index of obj |
| `path(expr)` | Returns the path(s) that expr produces |
| `paths` | All paths in input; `paths(f)` filters by node type |
| `type` | Type name as string |
| `builtins` | List all builtin function names (with optional filter args) |

## Array/Object Transformation

| Function | Description |
|----------|-------------|
| `map(f)` | Apply f to each element, return array |
| `map_values(f)` | Apply f to each value, preserve input type (array/object) |
| `pick(paths)` | Build object from path expressions |
| `getpath(paths)` | Get value at path (takes array of paths) |
| `setpath(path; val)` | Set value at path |
| `delpaths(paths)` | Delete values at given paths |
| `del(path)` | Delete the path expression |
| `to_entries` | Object → array of `{key, value}` objects |
| `from_entries` | Array of `{key, value}` → object |
| `with_entries(f)` | Transform object via to_entries → f → from_entries |

## Aggregation

| Function | Description |
|----------|-------------|
| `add` | Sum numbers, concatenate arrays/strings, merge objects. `add(gen)` sums generator outputs |
| `any` | True if any element is truthy; `any(cond)` checks condition; `any(gen; cond)` on generator |
| `all` | True if all elements are truthy (same forms as `any`) |
| `min`, `max` | Minimum/maximum value |
| `min_by(f)`, `max_by(f)` | Min/max by key function |
| `flatten` | Flatten nested arrays; `flatten(n)` limits depth |
| `unique` | Sort and remove duplicates; `unique_by(f)` by key |
| `reverse` | Reverse array order |
| `sort` | Sort array; `sort_by(f)` sort by key function |
| `group_by(f)` | Group sorted array into subarrays (input must be pre-sorted by f) |
| `contains(x)` | Whether input contains x (works on strings, arrays, objects) |
| `inside(x)` | Inverse of contains — whether input is inside x |
| `combinations` | Cartesian product of array of arrays; `combinations(n)` takes n-tuples |
| `transpose` | Transpose matrix (array of arrays) |
| `bsearch(x)` | Binary search in sorted array |

## String Functions

| Function | Description |
|----------|-------------|
| `split(s)` | Split by separator string |
| `join(s)` | Join array elements with separator |
| `explode` | String → array of codepoint numbers |
| `implode` | Array of codepoints → string |
| `index(s)` | First index of substring; `rindex(s)` for last |
| `indices(s)` | All indices of substring |
| `startswith(s)`, `endswith(s)` | Prefix/suffix check |
| `ltrimstr(s)`, `rtrimstr(s)`, `trimstr(s)` | Remove prefix/suffix/both string |
| `trim`, `ltrim`, `rtrim` | Remove whitespace |
| `ascii_downcase`, `ascii_upcase` | Case conversion (ASCII only) |

## Math Functions

| Function | Description |
|----------|-------------|
| `abs` | Absolute value |
| `fabs` | Absolute value as float |
| `floor`, `ceil`, `round` | Rounding functions |
| `sqrt` | Square root |
| `sin`, `cos`, `tan` | Trigonometric functions |
| `asin`, `acos`, `atan`, `atan2` | Inverse trigonometric |
| `exp`, `log`, `log10` | Exponential and logarithmic |
| `pow(x)` | Raise to power x |
| `infinite`, `nan` | Special float values |
| `isinfinite`, `isnan`, `isfinite`, `isnormal` | Float predicates |
| `range(n)` | 0 to n-1; `range(a;b)` from a to b-1; `range(a;b;c)` with step c |

## JSON Conversion

| Function | Description |
|----------|-------------|
| `tojson` | Convert any value to its JSON string representation |
| `fromjson` | Parse JSON string back to value |
| `tojsonc` | Compact JSON output |

## Error/Control

| Function | Description |
|----------|-------------|
| `empty` | Produces no output (useful in generators) |
| `error` | Raise error; `error(msg)` with message |
| `halt` | Exit immediately with code 5 |
| `halt_error(n)` | Exit with code n, optionally printing message |
| `$__loc__` | Location info of current expression (filename, line, column) |

## Feature Detection

| Function | Description |
|----------|-------------|
| `have(feature)` | Check if feature is available (e.g., "oniguruma", "dev") |
| `have_decnum` | Whether arbitrary-precision decimal numbers are supported |
| `have_literal_numbers` | Whether original number literals are preserved |
| `$JQ_BUILD_CONFIGURATION` | Object with build configuration details |

## Environment

- `$ENV` — object of all environment variables (string values)
- `env` — same as `$ENV`
- Individual vars: `$ENV.PATH`, `$ENV.HOME`, etc.
