# I/O and Streaming

## input / inputs

Read additional JSON values from stdin or files.

- `input` — reads the next JSON value (one at a time)
- `inputs` — reads all remaining JSON values (generator, one per output)

Use with `-n` flag to prevent jq from consuming the first value as normal input:

```
jq -n 'input.name' file.json          # read first JSON object
jq -n '[inputs]' file1.json file2.json  # slurp all files into array
jq -n 'input | .name'                 # read one value from stdin
```

## input_filename / input_line_number

Metadata about the current input:

```
jq -n 'inputs | {file: input_filename, line: input_line_number, data: .}' *.json
```

- `input_filename` — name of file being read (null for stdin)
- `input_line_number` — line number of current JSON value in input

## debug / stderr

Send diagnostic output to stderr while passing main output through:

```
.data | debug              # prints . to stderr, passes through
.data | debug("label")     # prints with label prefix
.data | stderr             # sends . to stderr, produces no stdout output
```

Useful for debugging complex filters without polluting stdout.

## halt / halt_error

- `halt` — exit immediately with code 5
- `halt_error(n)` — exit with code n, optionally printing message to stderr
- `halt_error("message")` — exit with code 5 and print message

```
if .valid then . else halt_error("Invalid input") end
```

## Streaming Parse (`--stream`)

Parse JSON incrementally without loading entire document. Outputs `[path, value]` pairs:

```
jq --stream '[0].name' huge.json
```

For `{"a": [1, 2]}`, streaming produces:
- `[[], {"a": [...]}]` — top-level object start
- `[[0], []]` — empty array at path [0]
- `[[1, "a"], 1]` — value 1 at path [1, "a"]
- `[[1, "a"], 2]` — value 2 at path [1, "a"]

## fromstream / truncate_stream

Reconstruct JSON from streaming output:

```
# Process stream incrementally
jq -n --stream '
  fromstream(
    streams
    | truncate_stream(([0, "name"] | select(. != null)))
  )
'

# Reduce over stream for large files
jq -n --stream '
  reduce inputs as [$path, $val] (
    {total: 0};
    if ($path | last) == "price" then .total += $val else . end
  )
'
```

- `fromstream(expr)` — reconstruct JSON values from stream filtered by expr
- `truncate_stream(path_filter)` — stop streaming when path matches filter
- `tostream` — convert value to stream of `[path, value]` pairs
- `streams` — generator that yields all streams from input

## $ARGS

Access command-line arguments:

```
jq -n '$ARGS.named'           # --arg / --argjson values
jq -n '$ARGS.positional'       # --args / --jsonargs values
jq -n '$ARGS.flags'            # CLI flags as object
```

With `--arg name value`: `$name` and `$ARGS.named.name`
With `--argjson name 123`: `$name` is number 123
With `--args a b c`: `$ARGS.positional` is `["a","b","c"]`
With `--jsonargs 1 true`: `$ARGS.positional` is `[1, true]`

## $ENV / env

Access environment variables:

```
jq '$ENV.HOME'                # specific variable
jq '$ENV'                     # all env vars as object
jq 'env'                      # same as $ENV
```

All values are strings. Use `| tonumber` for numeric conversion.
