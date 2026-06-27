---
name: jq-1-8-2
description: jq 1.8.2 — lightweight command-line JSON processor. Use when the user needs to parse, query, transform, or manipulate JSON data from the command line, process API responses, extract fields from JSON, convert between formats (JSON-to-CSV, JSON-to-XML), validate JSON, or work with any structured data in JSON format. Covers filters, builtins, regex, modules, streaming, and all jq 1.8.2 features.
metadata:
  tags:
    - cli
    - json
    - data-processing
---

# jq 1.8.2

## Overview

`jq` is a lightweight, flexible command-line JSON processor written in C with zero runtime dependencies. Think of it as `sed`/`awk`/`grep` for JSON data. Version 1.8.2 includes significant security hardening (CVE fixes for buffer overflows, stack overflow guards, hash collision mitigation) and build improvements (Windows arm64, Docker arm/v7 support).

A jq program is a **filter**: it takes JSON input and produces JSON output. Filters chain with `|` (pipe), combine with `,` (comma), and support variables, conditionals, user-defined functions, regex, modules, and streaming.

## Usage

### Basic invocation

```bash
# Pretty-print / validate JSON
jq '.' file.json

# Extract a field
jq '.name' file.json

# Compact output (one JSON per line)
jq -c '.[]' file.json

# Raw string output (no quotes)
jq -r '.message' file.json

# NUL-delimited output (safe for filenames with newlines)
jq --raw-output0 '.path' file.json

# No newline after output
jq -j '.id' file.json

# Read from stdin
echo '{"a":1}' | jq '.a'

# Multiple files
jq '.name' file1.json file2.json

# Load filter from file
jq -f filter.jq data.json

# Pass string arguments
jq --arg name "Alice" '.name == $name' data.json

# Pass JSON arguments (parsed, not stringified)
jq --argjson age 30 '.age > $age' data.json

# Read a file as array of JSON values
jq --slurpfile config config.json '. + $config[0]' data.json

# Read raw file content as string
jq --rawfile tmpl template.html '$tmpl' null

# Environment variables
jq '$ENV.PATH' null

# Slurp all inputs into one array
jq -s 'map(.name)' file1.json file2.json

# Don't read input (use null as input, good for constructing JSON)
jq -n '{version: "1.0", items: [1,2,3]}'

# Raw input (each line becomes a string, not parsed as JSON)
jq -R 'split(",")' <<< "a,b,c"

# Exit status based on output truthiness
jq -e '.valid' file.json  # 0 if true, 1 if false/null, 4 if no output

# Sort object keys in output
jq -S '.' file.json

# Tab indentation
jq --tab '.' file.json

# Custom indentation (1-7 spaces)
jq --indent 4 '.' file.json

# Streaming parse for very large inputs
jq --stream '[0].name' huge.json

# JSON-seq mode (RS/LF delimiters, skips parse errors)
jq --seq '.valid // false' stream.json

# Color output control
jq -C '.' file.json   # force color
jq -M '.' file.json   # monochrome (no color)
```

### Core filter patterns

```bash
# Identity (pretty-print / validate)
jq '.'

# Object field access
jq '.foo'           # dot notation (identifier-like keys only)
jq '."foo-bar"'     # quoted key
jq '.["foo-bar"]'   # bracket notation (any key)
jq '.foo.bar.baz'   # chained (same as .foo | .bar | .baz)

# Optional field access (no error if missing/wrong type)
jq '.foo?'          # returns null instead of error

# Array indexing
jq '.[0]'           # first element
jq '.[-1]'          # last element
jq '.[2:5]'         # slice (indices 2,3,4)
jq '.[:3]'          # first 3 elements
jq '.[-2:]'         # last 2 elements

# Iterate over array/object values
jq '.[]'            # each element of array, or each value of object
jq '.items[] | .name'  # pipe each item through filter

# Recursive descent (all values at all depths)
jq '.. | .name?'    # find all "name" fields anywhere in structure

# Comma (produce multiple outputs from same input)
jq '.foo, .bar'     # output foo, then bar

# Select matching elements
jq '.[] | select(.active == true)'
jq '.[] | select(.age > 18)'
jq '[.[] | select(.type == "user")]'  # collect into array

# Map (apply filter to each element)
jq 'map(.name | ascii_upcase)'
jq 'map_values(.price * 0.9)'   # same as map but preserves object shape

# Conditional
jq 'if .status == "ok" then .data else .error end'

# Alternative operator (//) — use right side if left is null or false
jq '.optional // "default"'

# Try-catch / error suppression
jq '.value? // 0'        # ? suppresses errors
jq 'try .parse | catch "failed"'

# Variable binding
jq '.name as $n | select(.type == $n)'

# Reduce (fold array into single value)
jq '[.items[] | .price] | add / length'   # average price
jq 'reduce .items[] as $item (0; . + $item.price)'  # total price

# Group and sort
jq 'group_by(.category) | map({cat: .[0].category, count: length})'
jq 'sort_by(.date) | reverse'

# String interpolation
jq '"User \(.name) is \(.age) years old"'

# Regex operations
jq '.email | test("^[^@]+@[^@]+$")'
jq '.text | gsub("[0-9]"; "*")'
jq '.html | capture("<h1>(?<title>.*)</h1>")'

# User-defined functions
jq 'def double: . * 2; [items[] | double]'

# Object construction / transformation
jq '{name, email}'                    # shorthand for {name: .name, email: .email}
jq '{(.key): .value}'                # dynamic key from expression
jq '. + {"new_field": 42}'           # merge objects (right wins on conflict)
jq '. * {"nested": {"a": 1}}'        # recursive merge

# Type checking / conversion
jq 'select(type == "array")'
jq 'map(tostring)'
jq 'map(tonumber)'
```

### Common patterns

```bash
# CSV to JSON (with headers)
jq -R -s 'split("\n") | .[1:] | map(split(",") | {name:.[0], age: (.[1]|tonumber)})' file.csv

# JSON to CSV
jq -r '[.name, .age] | @csv' file.json

# JSON to TSV
jq -r '[.name, .age] | @tsv' file.json

# JSON to XML (built-in format)
jq '@xml' file.json

# Base64 encode/decode
jq '.data | @base64'       # encode
jq '"hello" | @base64d'    # decode

# URL encoding
jq '.query | @uri'         # encode
jq '"hello%20world" | @uri'  # (already encoded, stays same)

# Date formatting
jq '.timestamp | strftime("%Y-%m-%d %H:%M:%S")'

# Construct JSON from scratch
jq -n '{users: [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}'

# Merge two JSON files
jq -s '.[0] * .[1]' file1.json file2.json

# Filter array by multiple conditions
jq '[.[] | select(.active and .age >= 18 and (.role == "admin" or .role == "editor"))]'

# Unique values
jq '[.items[].tag] | unique'

# Count occurrences
jq 'group_by(.status) | map({status: .[0].status, count: length})'

# First/last/nth element
jq '.[0:1] | .[0]'        # first
jq '.[-1:] | .[0]'        # last
jq 'nth(5; .[])'          # 6th element (0-indexed)
jq 'limit(10; .[])'       # first 10 elements

# Deep path queries
jq 'paths(type == "string")'    # paths to all string values
jq 'getpath(["user", "name"])'  # same as .user.name
jq 'setpath(["user", "role"]; "admin")'  # set nested value
jq 'del(.metadata.cache)'      # delete a key

# Working with null
jq '.optional // empty'    # produce no output if null/false
jq 'map(select(. != null))'  # filter out nulls
```

### Modules

```bash
# Import a module
# In your jq file: import "./mylib" as lib; lib.myfunc

# Include a module (functions become available directly)
# include "std"; my_builtin_func

# Specify library search path
jq -L ./lib -f program.jq data.json
```

## Gotchas

- **Always single-quote jq filters on Unix** — `jq '.foo'` not `jq .foo`. The shell interprets `.`, `$`, `*`, `[]`, etc. as special characters. On Windows cmd.exe, use double quotes and escape inner double quotes.
- **`.foo` only works for identifier-like keys** — keys with hyphens, spaces, or starting with digits need `."key"` or `.["key"]` syntax.
- **`.` in a pipeline refers to the current value at that point**, not the original input. Use `as $var` to save the original.
- **Pipe is a cartesian product** — if left side produces N results and right side produces M per result, you get N×M outputs, not N+M.
- **`select(false)` produces no output** (not `null`). Use `select(. != null)` to filter nulls, or `// empty` for null/false suppression.
- **`//` (alternative) triggers on both `null` AND `false`** — if you only want null fallback, use `if . == null then "default" else . end`.
- **`?` suppresses all errors**, not just missing keys. Use carefully — it can hide real bugs.
- **`map(f)` always returns an array**; `map_values(f)` preserves the input type (array stays array, object stays object).
- **Numbers lose precision after arithmetic** — jq stores literal numbers with original precision but converts to IEEE754 double on any operation. Use `have_decnum` to check if your build supports arbitrary-precision decimals.
- **Object merge with `+` is shallow** — use `*` for recursive/ deep merge.
- **`group_by` requires sorted input** — the array must be pre-sorted by the grouping key, or use `sort_by(.key) | group_by(.key)`.
- **`recurse` can infinite-loop** on circular data. Use `recurse(f; condition)` to limit depth.
- **Regex requires Oniguruma support** — check with `jq -n 'have("oniguruma")'`. Most prebuilt binaries include it.
- **`inputs` reads remaining JSON values** from stdin/files after the first one (which is the normal input). Use with `-n` flag.
- **`--stream` outputs `[path, value]` pairs** — you need to reconstruct the structure with `reduce`/`foreach` or use `fromstream`.
- **jq 1.8.2 limits array/object size to 2²⁹ elements** and path depth for security. Deeply nested structures may hit these limits.

## References

- [01-filters-and-operators](references/01-filters-and-operators.md) — Basic filters, operators, types, and values
- [02-builtin-functions](references/02-builtin-functions.md) — Complete list of built-in functions by category
- [03-conditionals-and-control-flow](references/03-conditionals-and-control-flow.md) — if-then-else, try-catch, select, reduce, foreach, while, until
- [04-regex](references/04-regex.md) — Regular expression functions: test, match, capture, scan, split, sub, gsub
- [05-advanced-features](references/05-advanced-features.md) — Variables, destructuring, def functions, scoping, generators, assignment operators
- [06-io-and-streaming](references/06-io-and-streaming.md) — input/inputs, debug, stderr, streaming parse, fromstream/tostream
- [07-modules](references/07-modules.md) — import, include, module declarations, library paths, modulemeta
- [08-cli-options](references/08-cli-options.md) — Complete command-line option reference with examples
- [09-formats-and-escaping](references/09-formats-and-escaping.md) — @csv, @tsv, @sh, @base64, @html, @json, @text, @uri, @xml, string interpolation
- [10-dates-and-math](references/10-dates-and-math.md) — Date/time functions, math library (sin, cos, exp, log, etc.)
