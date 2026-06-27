# Advanced Features

## Variable Binding

`expr as $var | body` — evaluates expr, binds result to `$var`, then evaluates body.

```
.name as $n | select(.type == $n)
[1,2,3] as $arr | length    # $arr available in body, . is original input
```

Multiple bindings chain:

```
.a as $a | .b as $b | $a + $b
```

Variable scope: `$var` is available in the rest of the pipeline and in nested expressions (functions, subfilters).

## Destructuring with `?//`

Destructuring alternative operator — binds variable if value exists, uses default otherwise.

```
.foo ?// $x as $val | ...    # bind .foo to $val if it exists and is not null/false
```

## User-Defined Functions

Define with `def`, use like builtins:

```
def double: . * 2;
[items[] | double]

def square: . * .;
def cube: . | square | . * input;   # can call other defs

# With parameters
def add($x; $y): . + $x + $y;
add(1; 2)    # . + 1 + 2

# Multiple parameters
def merge($a; $b; $c): $a + $b + $c;
```

- `def` must appear before use
- Parameters use `$name` syntax
- Body is a filter that receives input (`.`)
- Can define multiple functions in one `def` block: `def f: ...; g: ...; h: ...;`

## Scoping

Variables and function definitions have scope rules:

- Variables defined with `as` are available in the rest of the pipeline
- Function definitions are available from their point of definition onward
- Variables do not leak into subexpressions that were already evaluated before the binding
- Use parentheses to control scope: `(expr as $v | body)` limits `$v` to the parenthesized block

## isempty

`isempty(expr)` — returns true if expr produces no output.

```
isempty(.optional)      # true if .optional is null/missing
isempty([.[] | select(.active)])   # true if no active items
```

## Assignment Operators

### Update-assignment (`|=`)

Updates the value at a path by applying a filter to the existing value:

```
.items[0].name |= ascii_upcase        # update specific field
.foo |= . + 1                         # increment
.map(. * 2)                           # map over array values
```

### Arithmetic update-assignment

Shorthand for common patterns:

```
.count += 1           # same as .count |= . + 1
.price -= 5           # same as .price |= . - 5
.items *= 2           # multiply
.ratio /= 2           # divide
.mod %= 10            # modulo
.val //= "default"    # alternative (null/false → default)
```

### Plain assignment (`=`)

Replace value at path with new value:

```
.name = "Alice"               # set field
.[0] = "first"                # set array element
.foo.bar = 42                 # create nested path
```

### Complex assignments

Assignments work on generators and can affect multiple paths:

```
[.a, .b] = [1, 2]            # assign to multiple paths
.items[] |= . + 1             # update all items
.paths(type=="number") |= . * 2   # double all numbers
```

## Generators and Iterators

Filters that produce multiple outputs are generators:

- `.[]` — iterates array elements
- `,` — produces outputs from both sides
- `range(n)` — produces 0, 1, ..., n-1
- User functions can be generators: `def twiddle: "a", "b";`

Generators feed into pipelines. If a generator produces N values, the next filter runs N times.

```
range(3) | . * 2             # 0, 2, 4
[1,2,3] | .[] | . + 1       # 2, 3, 4
```

## SQL-Style Operators

jq supports SQL-like joins:

- `a | b` — pipe (like function composition)
- `[a, b] | group_by(.)` — union
- Cross product: `(.a[] , .b[])` produces cartesian product
- Semi-join: `.a[] | select(. as $x | .b[] | select(. == $x))`
