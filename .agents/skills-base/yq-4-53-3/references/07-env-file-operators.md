# Environment Variable and File Operators Reference

Inject environment variables and load external files into documents.

## `env(name)` — typed environment variable

Parses the value as YAML (booleans, numbers, maps, arrays are auto-detected):

```bash
COUNT=5 yq -n '.count = env(COUNT)'        # → 5 (number)
ENABLED=true yq -n '.enabled = env(ENABLED)' # → true (boolean)
OBJ='{a: 1}' yq -n '.config = env(OBJ)'     # → {a: 1} (map)
```

## `strenv(name)` — string environment variable

Always returns a string, regardless of content:

```bash
ENABLED=true yq -n '.flag = strenv(ENABLED)'  # → "true" (quoted string)
NAME=mike yq -i '.name = strenv(NAME)' file.yml
```

## `envsubst` — interpolate variables in strings

Replaces `${VAR}` or `$VAR` patterns inside strings:

```bash
yq '(.. | select(tag == "!!str")) |= envsubst' template.yml
```

Options for error handling:
- `nu` (NoUnset) — fail if variable is unset
- `ne` (NoEmpty) — fail if variable is empty
- `ff` (FailFast) — abort on first failure

```bash
yq '.msg |= envsubst(ne, ff)' template.yml
```

## `load(path)` — load YAML file

Load another YAML file as a value:

```bash
yq -n 'load("config/base.yml") * load("config/override.yml")'
yq '.defaults = load("defaults.yml")' main.yml
```

Path can be dynamic (use string operators):

```bash
yq '.[] | .data = load(.path)' registry.yml
```

## Format-specific loaders

```bash
load_xml(path)     # load XML file
load_props(path)   # load properties file
load_str(path)     # load plain text as string
load_base64(path)  # load base64-encoded UTF-8
```

## `fileIndex` — identify files in eval-all

When using `eval-all`, `fileIndex` returns the 0-based index of the current file:

```bash
yq ea 'select(fileIndex==0).a = select(fileIndex==1).b | select(fileIndex==0)' a.yml b.yml
```

## `documentIndex` — identify documents in multi-doc files

For multi-document YAML files, `documentIndex` returns the 0-based document index:

```bash
yq 'select(documentIndex == 0)' multi-doc.yml
```

## Security flags

Disable dangerous operations when processing untrusted input:

```bash
yq --security-disable-env-ops '.x = env(SECRET)' file.yml   # env() blocked
yq --security-disable-file-ops 'load("secret.yml")'          # load() blocked
```
