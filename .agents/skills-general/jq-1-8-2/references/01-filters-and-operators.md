# Filters and Operators

## Identity

`.` — the identity filter. Takes input, produces same value as output. Main use: pretty-printing and validating JSON.

```
echo '{"a":1}' | jq '.'   # formats and validates
```

## Object Access

| Syntax | Description |
|--------|-------------|
| `.foo` | Access field `foo` (identifier-like keys only: alphanumeric + underscore, no leading digit) |
| `."foo-bar"` | Quoted key access for non-identifier keys |
| `.["key"]` | Bracket notation — works for any key string |
| `.foo.bar` | Chained access (equivalent to `.foo \| .bar`) |
| `.foo?` | Optional access — returns null instead of error if field missing or not an object |

## Array Access

| Syntax | Description |
|--------|-------------|
| `.[0]` | Index by position (zero-based) |
| `.[-1]` | Negative index counts from end |
| `.[2:5]` | Slice — indices 2,3,4 (end exclusive) |
| `.[:3]` | From start to index 3 |
| `.[-2:]` | Last two elements |
| `.[]` | Iterate all elements (produces one output per element) |
| `.[]?` | Safe iteration — no error if input is not array/object |

## Recursive Descent

`..` — produces every value at every depth. Same as zero-argument `recurse`.

```
jq '.. | .name?'   # find all "name" fields anywhere in structure
```

Note: `..a` does not work. Use `.. | .a?` instead.

## Comma Operator

`,` — feeds same input to both sides, concatenates output streams.

```
jq '.foo, .bar'        # outputs foo value, then bar value
jq '.[4,2]'            # outputs element at index 4, then index 2
```

## Pipe Operator

`|` — feeds output(s) of left filter into input of right filter. If left produces N results, right runs N times.

```
jq '.items[] | .name'   # extract name from each item
```

Note: `.` in a pipeline refers to the current value at that point, not the original input.

## Arithmetic Operators

| Operator | Numbers | Arrays | Strings | Objects |
|----------|---------|--------|---------|---------|
| `+` | Add | Concatenate | Join | Merge (right wins on conflict) |
| `-` | Subtract | Remove elements | — | — |
| `*` | Multiply | — | Repeat N times | Recursive merge |
| `/` | Divide | — | Split by separator | — |
| `%` | Modulo | — | — | — |

`null` added to any value returns the other value unchanged.

## Comparison Operators

- `==`, `!=` — equality (works across types for same-value comparisons)
- `<`, `<=`, `>`, `>=` — ordering (numbers vs numbers, strings vs strings)
- `and`, `or`, `not` — boolean logic
- `//` — alternative operator: `$a // $b` returns `$b` if `$a` is `null` or `false`

## Array Construction

`[expr]` — collects all outputs of expr into a single array.

```
[.items[] | .name]        # collect all names into array
[1, 2, 3]                 # literal array (uses comma operator inside [])
```

## Object Construction

```
{a: 1, b: 2}              # explicit key-value pairs
{name, age}               # shorthand for {name: .name, age: .age}
{($key): .value}          # dynamic key (parentheses required)
"foo" as $k | {$k: 42}    # variable as key uses value as key name
```

When a value expression produces multiple results, multiple objects are produced.

## Type Predicates

These filters pass values of the given type and suppress others:

- `arrays` — only arrays
- `objects` — only objects
- `booleans` — only true/false
- `numbers` — only numbers
- `strings` — only strings
- `nulls` — only null
- `values` — everything except null
- `scalars` — numbers, strings, booleans (not arrays/objects/null)
- `normals` — finite numbers (not NaN or infinity)
- `finites` — finite numbers and zero

```
jq '.[] | select(type == "array")'   # filter by type string
jq 'arrays'                           # pass only arrays
```

## Type Conversion

- `tonumber` — parse string as number
- `tostring` — convert any value to string
- `toboolean` — null/0/"" → false, everything else → true
- `type` — returns type name as string ("null", "boolean", "number", "string", "array", "object")
