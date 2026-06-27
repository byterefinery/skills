# Traverse (Read) Reference

Navigate deeply into YAML, JSON, and other structured data using jq-style path expressions.

## Simple map navigation

```bash
yq '.a' file.yml        # read key "a"
yq '.a.b.c' file.yml    # nested traversal
```

## Splat operator

`[]` iterates over array elements or object values.

```bash
yq '.items[]' file.yml     # each element of array
yq '.config[]' file.yml    # each value in a mapping
```

**Optional splat** `.[*]` won't error on scalars:

```bash
yq '.[*]' scalar.yml   # safe on any node type
```

## Array indexing

```bash
yq '.[0]'           # first element
yq '.[-1]'          # last element (negative indices)
yq '.[0, 2]'        # multiple indices
yq '.[1:3]'         # slice from index 1 to 2
```

## Special characters in keys

Use quoted bracket notation for keys with dots, spaces, or special chars:

```bash
yq '.["key.with.dots"]' file.yml
yq '.["red rabbit"]' file.yml
yq '.["{}"]' file.yml
```

## Dynamic keys

Expressions inside `[]` are evaluated:

```bash
yq '.[.b]' file.yml        # use value of .b as key
yq '.[.config.keyName]'    # dynamic lookup
```

## Wildcard matching

Glob patterns (`*`) match keys:

```bash
yq '.a."*a*"' file.yml     # keys containing "a"
yq '."*port"' file.yml      # all keys ending in "port"
```

## Optional identifier

`?` suppresses errors when a path doesn't exist:

```bash
yq '.a?.b' file.yml    # no error if .a is missing
```

## Merge anchors

yq traverses merge anchors (`<<:`) by default. The `--yaml-fix-merge-anchor-to-spec` flag changes override semantics (earlier keys win per YAML 1.2 spec).

```bash
# Default (legacy): later merge anchor overrides
yq '.merged.thing' file.yml

# Spec-compliant: earlier merge anchor wins
yq --yaml-fix-merge-anchor-to-spec '.merged.thing' file.yml
```

## Aliases

Aliases (`*name`) are dereferenced during traversal:

```bash
yq '.alias.b' file.yml     # traverses into aliased content
yq '.alias[]' file.yml     # splat alias children
```
