# Advanced Features Reference

Comments, style, tags, anchors/aliases, entries, and path operations.

## Comment operators

### Add comments

```bash
yq '.a comment "this is a" | .b comment "this is b"' file.yml
yq '.a head_comment "header" | .a item_comment "item note"' file.yml
```

Comment positions:
- `comment` — standard (below the key)
- `head_comment` — above the key
- `item_comment` — inline after the value

### Read comments

```bash
yq '.a | comment' file.yml
```

## Style operators

Control YAML output styling. Apply with `style = <value>`:

```bash
yq '... style = ""' file.yml           # default flow style (same as -P)
yq '.name style = "doubleQuote"'       # force double quotes
yq '.name style = "singleQuote"'       # force single quotes
yq '.list style = "flow"'              # inline: [a, b, c]
yq '.map style = "flow"'               # inline: {a: 1, b: 2}
yq '.text style = "literal"'           # block scalar (|)
yq '.text style = "folded"'            # folded scalar (>)
```

Recursive style on all nodes:

```bash
yq '... style = ""' file.yml   # reset all styles
```

## Tags

Read and write custom YAML tags:

```bash
yq '.a tag = "!timestamp"' file.yml    # set tag
yq '.a | tag' file.yml                 # read tag
yq '.a tag = null' file.yml            # remove tag
```

Select by tag:

```bash
yq '(.. | select(tag == "!!str")) |= envsubst' template.yml
```

## Anchors and aliases

### Create anchors

```bash
yq '.defaults anchor = "def"' file.yml
# Creates: &def
```

### Reference aliases

```bash
yq '.config alias = "def"' file.yml
# Creates: *def
```

### Explode anchors/aliases

Replace aliases with their full content:

```bash
yq '. | explode' file.yml
```

## Entries

Convert between key-value representation and entry objects:

```bash
yq '. | entries' file.yml
# {key: "a", value: "hello"} for each mapping entry

yq '. | from_entries' keys_values.yml
# Convert array of {key, value} back to map
```

## Path operations

### `path` — get the path to a node

```bash
yq '.items[] | select(.active) | path' data.yml
# Output: ["items", 0]
```

### `line` / `column` — source location

```bash
yq '.a | line' file.yml      # line number
yq '.a | column' file.yml    # column number
```

## Kind operators

Check node type:

```bash
yq '.[] | select(kind == "!!map")' data.yml
yq '.[] | select(kind == "!!seq")' data.yml
yq '.[] | select(tag == "!!str")' data.yml
```

## Recursive descent `..`

Glob all nodes at any depth:

```bash
yq '.. | select(tag == "!!str")' file.yml    # all strings
yq '.. |= upcase' file.yml                    # uppercase all scalars
```

## Sort

```bash
yq 'sort_keys' file.yml                        # sort mapping keys
yq '.items |= sort_by(.name)' data.yml         # sort array by field
yq '.items |= reverse' data.yml                # reverse array
yq '.items |= unique' data.yml                 # remove duplicates
```

## `with(path; expr)` — scoped update

Apply expression within a path scope:

```bash
yq 'with(.config; .timeout = 30 | .retries = 3)' file.yml
```
