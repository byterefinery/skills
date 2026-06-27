# String Operators Reference

Regex and string manipulation using Go's RE2 engine.

## Regex operators

### `test(regex)` — boolean match

```bash
yq '.[] | select(test("^[a-z]+$"))' data.yml
yq '.name | test("(?i)admin")'   # case-insensitive
```

### `match(regex)` — capture details

Returns match position, length, and captured groups.

### `capture(regex)` — named groups to map

```bash
yq '.url | capture("^(?<proto>\\w+)://(?<host>[^/]+)")' config.yml
# Output: {proto: "https", host: "example.com"}
```

### `sub(regex, replacement)` — substitute

```bash
yq '.name |= sub("cat"; "dog")' file.yml
yq '.path |= sub("/old/"; "/new/")' config.yml
```

Backreferences use `$<name>` or `$<number>`.

## String interpolation

Embed document values in strings using `\(.expr)`:

```bash
yq '.msg = "User \(.name) has \(.count) items"' data.yml
```

## String concatenation

Use `+` to join strings:

```bash
yq '.full = .first + " " + .last' people.yml
```

## String slicing (v4.53.1+)

Slice strings by index:

```bash
yq '"hello world"[0:5]'   # "hello"
yq -n '."hello world"[-5:]'  # "world"
```

## Length

```bash
yq '.name | length' file.yml
```

## Uppercase / Lowercase

```bash
yq '.name |= upcase' file.yml
yq '.name |= downcase' file.yml
```

## Explode (to array of characters)

```bash
yq '"hello" | explode'   # [104, 101, 108, 108, 111]
```

## Newlines in bash

Bash `$(cmd)` strips trailing newlines. Use alternatives:

```bash
# Method 1: printf
printf -v m "cat\n" ; m="$m" yq -n '.a = strenv(m)'

# Method 2: multiline assignment
m="cat
" yq -n '.a = strenv(m)'

# Method 3: IFS read
IFS= read -rd '' output < <(cat file)
output=$output yq '.data = strenv(output)' config.yml
```
