# Modules

## Module Declaration

A jq module is a `.jq` file that starts with a `module` declaration:

```jq
module { descriptor: "my library v1.0" };

def double: . * 2;
def triple: . * 3;
```

- `module` keyword with optional metadata object
- Functions defined in the module are available when imported/included
- Module file should have `.jq` extension

## include

Includes a module — its functions become available in the current scope:

```jq
include "std";        # from module search path
include "./helpers";  # relative to current file
include "lib" as $m;  # with alias (rarely needed for include)
```

- Resolved relative to the including file's directory
- Functions are available directly (no prefix needed)
- Multiple includes merge their definitions

## import

Imports a module with an alias — functions are accessed through the alias:

```jq
import "./math" as m;

.m | m.double | m.triple
```

- Functions accessed as `alias.function_name`
- Can also import as variable: `import "data.json" as $data;` (treats JSON file as data)

## Module Search Path

Control where jq looks for modules:

```bash
jq -L ./lib -f program.jq    # prepend ./lib to search path
jq -L ./lib1 -L ./lib2 -f program.jq  # multiple paths
```

Search order:
1. Directories specified by `-L` (in order given)
2. `~/.jq/`
3. System module directory (usually `/usr/local/lib/jq`)

When any `-L` is used, the default search path is replaced entirely.

## include vs import

| Feature | `include` | `import` |
|---------|-----------|----------|
| Functions available as | Direct names | Prefixed with alias |
| Use case | Extend current scope | Namespace isolation |
| Multiple definitions | Last one wins | No conflict (different namespaces) |

## modulemeta

Returns the metadata object of the current module:

```jq
modulemeta  # returns { descriptor: "my library v1.0" }
```

Useful for version checking or documentation.

## Example: Library Module

File `lib/math.jq`:

```jq
module {};

def square: . * .;
def cube: . | square | . * input;
def factorial:
  def f($n): if $n <= 1 then 1 else $n * f($n - 1) end;
  f(.);
```

Usage:

```bash
jq -L lib -n 'include "math"; 5 | factorial'
# Output: 120
```

Or with import:

```bash
jq -L lib -n 'import "math" as m; 5 | m.factorial'
```

## Gotchas

- Module paths are relative to the **including file**, not the working directory
- Circular imports cause errors (detected at compile time in jq 1.8)
- `include` and `import` must appear at the top level of a jq program
- When using `-f`, module paths resolve relative to the filter file, not stdin
