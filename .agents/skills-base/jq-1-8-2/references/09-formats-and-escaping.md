# Formats and Escaping

## String Interpolation

Use `\(expr)` inside double-quoted strings to embed expression results:

```
"name: \(.name), age: \(.age)"
"\(.items | length) items found"
"formatted: \(.value * 100 | floor)%"
```

- Expression is evaluated and converted to string
- Can contain pipes, function calls, etc.
- Multiple interpolations in one string are allowed

## Built-in Formats (`@format`)

Apply with `@format_name` syntax. Input type depends on format:

### @csv

Array → CSV string. Strings with commas/quotes/newlines are properly escaped.

```
["Alice", "30", "NY"] | @csv    # '"Alice","30","NY"'
```

### @tsv

Array → TSV (tab-separated) string.

```
["Alice", "30"] | @tsv          # "Alice\t30"
```

### @sh

Array → shell-escaped strings, one per element. Safe for command substitution.

```
["hello world", "foo;bar"] | @sh
# '"hello world"', '"foo;bar"'
```

### @base64 / @base64d

String ↔ base64 encoding/decoding.

```
"hello" | @base64       # "aGVsbG8="
"aGVsbG8=" | @base64d  # "hello"
```

### @html

Escape HTML special characters (`<`, `>`, `&`, `"`, `'`).

```
"<script>" | @html      # "&lt;script&gt;"
```

### @json / @text

- `@json` — same as `tojson` (convert value to JSON string)
- `@text` — identity (passes through unchanged, useful for format strings)

```
{a: 1} | @json          # '{"a":1}'
"hello" | @text         # "hello"
```

### @uri

URL-encode a string.

```
"hello world" | @uri    # "hello%20world"
```

### @xml

Convert array/object to XML-like format. First element is tag name, rest are attributes/content.

```
["div", {"class": "main"}, ["p", {}, "Hello"]] | @xml
# '<div class="main"><p>Hello</p></div>'
```

## Escaping Functions

| Function | Description |
|----------|-------------|
| `@csv` | Array → CSV string |
| `@tsv` | Array → TSV string |
| `@sh` | Array → shell-escaped strings |
| `@base64` | String → base64 |
| `@base64d` | Base64 → string |
| `@html` | HTML escape |
| `@json` | Value → JSON string |
| `@text` | Identity (passthrough) |
| `@uri` | URL encode |
| `@xml` | Array/object → XML |

## Common Conversions

```
# JSON array to CSV lines
[.[] | [.name, .age, .city] | @csv]

# CSV to JSON objects
-R -s 'split("\n") | .[1:] | map(split(",") | {name:.[0], age: (.[1]|tonumber), city: .[2]})'

# JSON to shell commands
.items[] | ["echo", .name] | @sh

# URL-safe JSON
tojson | @uri

# Base64 encode file content
--rawfile data file.bin | $data | @base64
```
