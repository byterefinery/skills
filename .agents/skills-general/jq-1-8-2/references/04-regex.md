# Regular Expressions

All regex functions use Oniguruma library (PCRE-compatible). Requires `have("oniguruma")` to be true.

## Flags

| Flag | Meaning |
|------|---------|
| `g` | Global — match all occurrences, not just first |
| `i` | Case-insensitive |
| `m` | Multiline — `^` and `$` match line boundaries |
| `s` | Dotall — `.` matches newlines |
| `p` | Perl-style — `^`/`$` match start/end of string, not lines |

## test

Returns boolean — whether regex matches the input string.

```
"hello" | test("hel")           # true
"hello" | test("HEL"; "i")      # true (case-insensitive)
.email | test("^[^@]+@[^@]+$")  # email validation
```

## match

Returns match object with `offset`, `length`, `string`, and `captures` fields. Produces one output per match with `g` flag.

```
"abc123def" | match("[0-9]+")
# {"offset": 3, "length": 3, "string": "123", "captures": [...]}

"abc123def456" | match("[0-9]+"; "g")
# Two outputs: one for "123", one for "456"
```

## capture

Extract named capture groups into an object. Named groups use `(?<name>...)` syntax.

```
"<h1>Hello</h1>" | capture("<h1>(?<title>.*)</h1>")
# {"title": "Hello"}

"2024-01-15" | capture("(?<y>\\d{4})-(?<m>\\d{2})-(?<d>\\d{2})")
# {"y": "2024", "m": "01", "d": "15"}
```

## scan

Find all non-overlapping matches of regex in string. Returns array of matched strings.

```
"abc123def456" | scan("[0-9]+")
# ["123", "456"]
```

## split (regex)

Split string by regex pattern (different from `split(string)` which splits by literal string).

```
"a,b; c:d" | split("[,;:]")
# ["a", "b", " c", "d"]
```

## splits

Like `split` but also produces the separators as alternating outputs. Useful for tokenizing.

```
"a,b,c" | splits(",")
# "a", ",", "b", ",", "c"
```

## sub / gsub

Replace regex matches with replacement string. Use `\\g<name>` or `\\0`-`\\9` for backreferences.

```
"hello world" | sub("world"; "jq")           # "hello jq"
"hello" | gsub("[aeiou]"; "*")               # "h*ll*"
"abc123" | gsub("(?<n>[0-9]+"); "\\g<n>!")   # "abc123!"
```

With flags:

```
"Hello WORLD" | sub("world"; "jq"; "i")      # "Hello jq"
```

## Common Patterns

```
# Email validation
test("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")

# Extract URLs
scan("https?://[^\\s]+")

# Remove HTML tags
gsub("<[^>]*>"; "")

# Parse key-value pairs
capture("(?<key>[^=]+)=(?<value>.+)")

# Split on whitespace
split("\\s+")

# Match IPv4
test("^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$")
```
