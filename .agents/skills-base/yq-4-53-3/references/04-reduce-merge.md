# Reduce and Merge Reference

Aggregate collections into new structures using `ireduce` and merge operators.

## `ireduce` syntax

```
<collection> as $<name> ireduce (<init>; <update>)
```

- `<collection>` — items to iterate (usually splatted with `[]`)
- `$<name>` — variable for each element
- `<init>` — starting accumulator value
- `<update>` — expression applied per element (`.` is the accumulator)

## Sum numbers

```bash
yq '.[] as $item ireduce (0; . + $item)' numbers.yml
```

## Merge all files

Use `eval-all` (alias: `ea`) to load all documents from all files:

```bash
yq ea '. as $item ireduce ({}; . * $item)' path/to/*.yml
```

Merge two specific files:

```bash
yq -n 'load("a.yaml") * load("b.yaml")'
```

## Convert array to object

```bash
yq '.[] as $item ireduce ({}; .[$item.name] = $item.value)' data.yml
```

## Collect into array

```bash
yq '[.[] | select(.active)]' data.yml
```

Or with `collect`:

```bash
yq '.items[] | select(.valid) | collect' config.yml
```

## Collect into object (group by key)

```bash
yq '.[] | group_by(.category) | .[0]' data.yml
```

## Multiply-merge `*`

The `*` operator deep-merges two structures:

```bash
yq -n '{a: 1, b: {x: 1}} * {b: {y: 2}, c: 3}'
# Output:
# a: 1
# b:
#   x: 1
#   y: 2
# c: 3
```

## Append to array `+=`

```bash
yq '.items += ["new_item"]' config.yml
```

## Pick and subtract

Select or remove specific keys:

```bash
yq 'pick(.a, .b.c)' file.yml      # keep only a and b.c
yq 'subtract(.deprecated_keys)'   # remove matching keys
```

## `first(exp)`

Return the first element matching an expression:

```bash
yq '.[] | first(select(.type == "primary"))' data.yml
```
