# Conditionals and Control Flow

## if-then-else-end

```
if .status == "ok" then .data
elif .status == "warn" then .message
else .error
end
```

- `if`/`then`/`elif`/`else`/`end` keywords
- Conditions are truthy if not `null` or `false`
- `else` branch is optional for single-branch ifs
- Nested ifs are allowed

## select

`select(cond)` passes input through only if condition is truthy (not null/false). Produces no output otherwise.

```
[.[] | select(.active == true)]       # filter active items
.select(.age > 18)                     # pipe form
```

Equivalent to `if cond then . else empty end`.

## try-catch

```
try .parse                              # suppress errors, produce no output on failure
try .parse // "default"                 # suppress errors, use alternative
try .parse | catch .message             # catch and inspect error
try .parse | catch "fallback"           # catch with constant fallback
```

- `try expr` — runs expr, produces no output if error occurs
- `try expr | catch handler` — on error, passes the error to handler

## Error Suppression (`?`)

Append `?` to any expression to suppress errors:

```
.foo?           # null if field missing
.[0]?           # null if not array or out of range
(1 / .val)?     # no error if .val is 0
```

Note: `?` suppresses **all** errors, not just type mismatches. Use carefully.

## Alternative Operator (`//`)

`$a // $b` — returns `$b` if `$a` produces `null` or `false`. Otherwise returns `$a`.

```
.optional // "default"
(.foo // .bar) // "fallback"    # chained fallbacks
```

Important: triggers on both `null` AND `false`. If you only want null fallback:

```
if . == null then "default" else . end
```

## reduce

Fold an array/generator into a single accumulator value.

```
reduce expr as $var (initial; update)
```

- `expr` — generates values to iterate over
- `$var` — bound to each generated value
- `initial` — starting accumulator
- `update` — expression that takes current accumulator (`.`) and `$var`, produces new accumulator

Examples:

```
# Sum prices
reduce .items[] as $item (0; . + $item.price)

# Build object from array
reduce keys[] as $k ({}; . + {($k): input[$k]})

# Find max
reduce .[] as $x (. [0]; if $x > . then $x else . end)
```

## foreach

Like `reduce` but emits intermediate states. Useful with `--stream`.

```
foreach expr as $var (initial; update; extractor)
```

- Same as reduce, plus `extractor` — expression applied to each intermediate state for output

Example: running totals

```
foreach .[] as $x (0; . + $x; .)
# Input: [1, 2, 3]
# Output: 1, 3, 6
```

## while / until

Loop constructs:

```
while(condition; update)     # loop while condition is truthy
until(condition; update)     # loop until condition becomes truthy
```

- `while(cond; upd)` — applies `upd` repeatedly while `cond` is true
- `until(cond; upd)` — applies `upd` repeatedly until `cond` becomes true

Examples:

```
0 | while(. < 10; . + 1)     # produces: 0, 1, 2, ..., 9
"hello" | while(length < 10; . + "!")   # "hello!!!!"
```

## recurse

Recursive descent through nested structures.

```
recurse                    # same as ..
recurse(f)                 # apply f to each value and recurse into results
recurse(f; condition)      # recurse only while condition is truthy
```

Examples:

```
recurse(.children?)        # walk tree structure
recurse(.[]?; . != [])     # recurse into arrays, stop at empty
recurse(.values[]?; length < 100)  # limit recursion depth
```

## isempty

`isempty(expr)` — returns `true` if expr produces no output, `false` otherwise.

```
isempty(.optional)         # true if .optional is missing/null
```

## first / last / nth / limit / skip

Control how many outputs a generator produces:

| Function | Description |
|----------|-------------|
| `first(expr)` | First output of expr |
| `last(expr)` | Last output of expr |
| `nth(n; expr)` | nth output (0-indexed) |
| `limit(n; expr)` | First n outputs of expr |
| `skip(n; expr)` | All outputs after first n |

Without arguments, `first`, `last`, `nth(n)` operate on the input stream.
