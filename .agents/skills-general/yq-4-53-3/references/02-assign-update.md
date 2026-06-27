# Assign (Update) Reference

Update node values using `=` (plain) or `|=` (relative) assignment.

## Plain assignment `=`

Sets LHS to the value of RHS evaluated against the current document:

```bash
yq '.a.b = "frog"' file.yml
yq '.a = .b' file.yml         # copy sibling
yq '(.a, .c) = "potato"' file.yml   # update multiple paths
```

## Relative assignment `|=`

RHS is evaluated with each LHS node as context. Useful for incremental updates:

```bash
yq '.[] |= . * 2' numbers.yml     # double each array element
yq '.a |= .b' file.yml            # set .a to value of .a.b
```

## Create nodes from scratch

Use `-n` (null input) to create documents without reading a file:

```bash
yq -n '.a.b = "cat" | .x = "frog"'
# Output:
# a:
#   b: cat
# x: frog
```

Empty objects and arrays are created automatically:

```bash
yq -n '.a.b.[0] = "bogs"'
# Output:
# a:
#   b:
#     - bogs
```

## Update deeply selected results

Wrap the LHS in parentheses when combining select/filter with assignment:

```bash
yq '(.[] | select(.name == "foo") | .address) = "12 cat st"' data.yaml
yq '(.a[] | select(. == "apple")) = "frog"' file.yml
```

## In-place editing

The `-i` flag writes changes back to the first input file:

```bash
yq -i '.version = "2.0"' config.yaml
```

Multiple updates in one pass (efficient for large files):

```bash
yq -i '
  .a.b[0].c = "cool" |
  .x.y.z = "foobar" |
  .person.name = strenv(NAME)
' file.yaml
```

## Custom tags

By default, custom YAML tags are preserved on the LHS node. Use `=c` to clobber:

```bash
yq '.a = .b' file.yml     # .a keeps its original tag (!cat)
yq '.a =c .b' file.yml    # .a gets .b's tag (!dog)
```

## Update from another file

Use `eval-all` with `fileIndex` to reference values from other files:

```bash
yq eval-all 'select(fileIndex==0).a = select(fileIndex==1).b | select(fileIndex==0)' main.yml overlay.yml
```
