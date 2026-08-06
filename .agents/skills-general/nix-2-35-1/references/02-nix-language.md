# Nix Language Reference

## Types

### Primitives

| Type | Example | Check |
|------|---------|-------|
| Integer | `42`, `0xFF` | `builtins.isInt` |
| Float | `3.14`, `.27e13` | `builtins.isFloat` |
| Boolean | `true`, `false` | `builtins.isBool` |
| String | `"hello"`, `''multi\nline''` | `builtins.isString` |
| Path | `./file.txt`, `/abs/path` | `builtins.isPath` |
| Null | `null` | `builtins.isNull` |

### Compound

| Type | Example | Check |
|------|---------|-------|
| Attribute set | `{ x = 1; y = "two"; }` | `builtins.isAttrs` |
| List | `[ 1 "two" { three = 3; } ]` | `builtins.isList` |
| Function | `x: x + 1` | `builtins.isFunction` |
| External | (created by plugins) | `builtins.isExternal` |

### Path literals

- Must contain at least one `/` to be recognized as a path
- `builder.sh` is attribute access; `./builder.sh` is a path
- Relative paths resolve against the [base directory](https://nix.dev/manual/nix/stable/#base-directory)
- `~/foo` expands home directory (not allowed in pure evaluation)
- Interpolating a path into a string copies the file to the store

## String Literals

### Double-quoted strings

```nix
"hello world"
"line1\nline2\ttab"
"escape \"quote\" and \${dollar-curly}"
```

Escape sequences: `\"`, `\\`, `\${`, `\n`, `\r`, `\t`. `$${` writes literal `$\${`.

### Indented strings (multi-line)

Enclosed in `''`. Strips common leading whitespace from each line.

```nix
''
  This is indented.
  So is this.
    This has extra indent.
''
# → "This is indented.\nSo is this.\n  This has extra indent.\n"
```

Escape in indented strings: `''` (literal single quote), `''${` (literal `${`), `''\\` (literal backslash).

### URI literals

```nix
"git+https://github.com/NixOS/nix"
# equivalent to the string above
```

## String Interpolation

`${expr}` inside strings, paths, or attribute names.

```nix
"--flag=${package}/lib"          # string: concatenation + store copy
"${pkgs.hello}/bin/hello"        # path in string → store path
./file-${version}.txt            # path interpolation
```

To write literal `${`:
- In double-quoted strings: `\${`
- In indented strings: `''${`
- `$${` works in both (produces `$\${`)

## Operators

Precedence (1 = highest):

1. `attrset.attrpath` — attribute selection (`.`, `. or default`)
2. `func arg` — function application (no symbol, whitespace)
3. `-num` — arithmetic negation
4. `attrset ? attrpath` — has attribute test
5. `list ++ list` — list concatenation (right-associative)
6. `*`, `/` — multiplication, division (left-associative)
7. `+`, `-` — addition, subtraction; also string/path concatenation
8. `!bool` — logical negation
9. `attrs // attrs` — attribute set update (right-associative)
10. `<`, `<=`, `>`, `>=` — comparison
11. `==`, `!=` — equality
12. `&&` — logical AND (left-associative)
13. `||` — logical OR (left-associative)
14. `->` — logical implication (right-associative)
15. `\|>`, `<\|` — pipe operators (experimental)

### Attribute set update (`//`)

Merges two attribute sets. Right side wins on conflicts.

```nix
{ a = 1; b = 2; } // { b = 3; c = 4; }
# → { a = 1; b = 3; c = 4; }
```

## Syntax

### Attribute Sets

```nix
{
  x = 123;
  text = "Hello";
  nested.attr = "value";
  a.b.c = 1;    # shorthand for nested sets
  a.b.d = 2;
}
```

Attribute paths (`a.b.c = val`) create nested structures automatically.

### Recursive Sets (`rec`)

Attributes can reference other attributes within the same set.

```nix
rec {
  x = 10;
  y = x + 5;    # y = 15
}
```

### Let Expressions

Bind names for use in a body expression.

```nix
let
  x = 10;
  y = x + 5;
in
  y * 2         # → 30
```

Functions in let:

```nix
let
  f = x: x * 2;
in
  f 21          # → 42
```

### With Expressions

Import all attributes of a set into scope. Creates *implicit* definitions.

```nix
with builtins;
  head [ 1 2 3 ]    # → 1

with import <nixpkgs> {};
  hello + vim       # string concatenation of store paths
```

Avoid overuse — implicit definitions can shadow unexpectedly and break referential transparency.

### Functions

Single-parameter lambda:

```nix
x: x + 1

{ name, version, ... }: {
  pname = name;
  inherit version;
}
```

Multi-parameter (curried):

```nix
x: y: x + y
# or destructured:
{ x, y }: x + y
```

Default arguments:

```nix
{ name ? "world" }: "Hello, ${name}!"
```

`...` in parameter set ignores extra attributes.

### If Expressions

```nix
if condition then expr1 else expr2

if pkgs.stdenv.isLinux then pkgs.linux-toolchain else null
```

### Assert Expressions

```nix
assert condition; expr

assert version >= 2; { inherit version; }
```

### Inherit

Shorthand for self-referencing attributes.

```nix
let
  name = "hello";
  version = "2.12";
in
{
  inherit name version;
  # equivalent to: name = name; version = version;
}

# From another set:
inherit (pkgs) hello vim;
# equivalent to: hello = pkgs.hello; vim = pkgs.vim;
```

### Parentheses

Function calls in lists need parentheses:

```nix
[ (f { x = 1; }) ]   # one element: result of f
[ f { x = 1; } ]     # two elements: f and { x = 1; }
```

## Scoping

- **Static (lexical) scoping** — variable values determined by enclosing scope at definition time
- **Explicit definitions** (let, rec, function params) can shadow any definition
- **Implicit definitions** (with) can only shadow other implicit definitions
- Builtins form the outermost scope

```nix
let x = 1; in
let x = 2; in
x    # → 2 (inner let shadows outer)
```

## Derivation Expression

The core construct for describing builds:

```nix
derivation {
  name = "hello-world";
  system = builtins.currentSystem;
  builder = "/bin/sh";
  args = [ "-c" "echo Hello > $out" ];
}

# Or the legacy form:
{ stdenv, ... }:
stdenv.mkDerivation {
  name = "my-package-1.0";
  src = ./source;
  buildInputs = [ pkgs.python3 ];
  buildPhase = ''
    make
  '';
  installPhase = ''
    make install PREFIX=$out
  '';
}
```

Required attributes: `name`, `system`, `builder`.
Optional: `args`, `env`, `inputs`, `outputHash`, `outputHashAlgo`, `outputMagicMime`, `outputs` (default `["out"]`).
