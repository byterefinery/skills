# Select and Filter Reference

Filter arrays and maps using boolean expressions.

## `select(expr)`

Returns nodes where the expression evaluates to true:

```bash
yq '.[] | select(.name == "foo")' data.yaml
yq '.items[] | select(.active == true)' config.yml
```

## Wildcard matching in select

Glob patterns work inside select:

```bash
yq '.[] | select(. == "*at")'       # ends with "at"
yq '.[] | select(. == "go*")'       # starts with "go"
yq '.[] | select(. == "*go*")'      # contains "go"
```

## Regex matching in select

Use `test()` for regex-based filtering:

```bash
yq '.[] | select(test("[a-zA-Z]+_[0-9]$"))' data.yml
```

## Comparison operators

```
==    !=     <    >    <=    >=
```

```bash
yq '.[] | select(.age >= 18)' users.yml
yq '.[] | select(.score > 50 and .active == true)' data.yml
```

## Boolean operators

```
and   or   not   any   all   empty
```

```bash
yq '.[] | select(.a > 5 and .b < 10)'
yq '.[] | select(.type == "cat" or .type == "dog")'
yq '.[] | select(not .disabled)'
```

## `filter(expr)`

Similar to select but preserves the array structure:

```bash
yq '.items | filter(.active == true)' config.yml
```

## `has(key)`

Check if a key exists:

```bash
yq '.[] | select(has("password"))' users.yml
```

## `contains(value)`

Check if node contains a substructure:

```bash
yq '.[] | select(contains({type: "admin"}))' roles.yml
```

## Delete nodes

Use `del()` to remove matching nodes:

```bash
yq 'del(.a.b)' file.yml
yq 'del(.items[] | select(.deprecated == true))' config.yml
yq 'del(."*temp*")' file.yml     # delete keys matching glob
```
