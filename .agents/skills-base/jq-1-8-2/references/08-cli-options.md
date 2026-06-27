# CLI Options Reference

## Input Options

| Option | Short | Description |
|--------|-------|-------------|
| `--null-input` | `-n` | Don't read input; use `null` as input. Use for constructing JSON from scratch |
| `--raw-input` | `-R` | Read each line as a raw string (not parsed as JSON) |
| `--slurp` | `-s` | Read all inputs into one array |
| `--stream` | | Parse incrementally, output `[path, value]` pairs for large files |
| `--stream-errors` | | Like `--stream` but yields error values for invalid JSON |
| `--seq` | | Use `application/json-seq` MIME type (RS/LF delimiters, skips parse errors) |
| `--binary` | `-b` | Prevent CRLF conversion on Windows WSL/MSYS2/Cygwin |

## Output Options

| Option | Short | Description |
|--------|-------|-------------|
| `--compact-output` | `-c` | One JSON value per line (no pretty-printing) |
| `--raw-output` | `-r` | Print strings without quotes (raw text output) |
| `--raw-output0` | | Like `-r` but NUL-delimited instead of newline-delimited |
| `--join-output` | `-j` | Like `-r` but no trailing newline |
| `--ascii-output` | `-a` | Escape all non-ASCII characters to `\uXXXX` |
| `--sort-keys` | `-S` | Output object keys in sorted order |
| `--color-output` | `-C` | Force colored output (even when piping) |
| `--monochrome-output` | `-M` | Disable colored output |
| `--tab` | | Use tabs for indentation instead of spaces |
| `--indent N` | | Use N spaces for indentation (1-7) |
| `--unbuffered` | | Flush output after each JSON value |

## Argument Passing

| Option | Description |
|--------|-------------|
| `--arg name value` | Pass string argument as `$name` |
| `--argjson name json` | Pass parsed JSON value as `$name` |
| `--slurpfile var file` | Read all JSON from file into `$var` as array |
| `--rawfile var file` | Read raw file content into `$var` as string |
| `--args` | Remaining args are positional strings in `$ARGS.positional` |
| `--jsonargs` | Remaining args are parsed JSON values in `$ARGS.positional` |

## Filter Options

| Option | Short | Description |
|--------|-------|-------------|
| `--from-file` | `-f` | Read filter from file instead of command line |
| `--library-path dir` | `-L` | Prepend directory to module search path |

## Exit Status

| Option | Short | Description |
|--------|-------|-------------|
| `--exit-status` | `-e` | Exit 0 if last output is truthy, 1 if false/null, 4 if no output |
| `--run-tests [file]` | | Run test file (input/output pairs) |

## Other

| Option | Short | Description |
|--------|-------|-------------|
| `--version` | `-V` | Print version and exit |
| `--build-configuration` | | Print build config and exit |
| `--help` | `-h` | Print help and exit |
| `--` | | End of options; remaining args are not parsed as flags |

## JQ_COLORS

Control syntax highlighting colors via environment variable:

```
JQ_COLORS="keys_color:strings_color:numbers_color:booleans_color:null_color:operators_color:separators_color"
```

Example with truecolor support:

```bash
JQ_COLORS="38;2;255;173;173:38;2;255;214;165:38;2;253;255;182:38;2;202;255;191:38;2;155;246;255:38;2;160;196;255:38;2;189;178;255:38;2;255;198;255"
```

## Common Combinations

```bash
jq -r '.[] | "\(.name): \(.email)"'     # raw output with string interpolation
jq -s 'add' file1.json file2.json        # slurp and merge
jq -R -s 'split("\n") | map(select(length > 0))'  # read text, split lines, filter empties
jq -c -r '.[] | @csv'                    # compact CSV output
jq -S -c '.'                             # deterministic JSON output (sorted keys, compact)
```

## Shell Quoting Rules

- **Unix shells**: Always single-quote the filter: `jq '.foo'`
- **Windows cmd.exe**: Use double quotes: `jq ".foo"`
- **PowerShell**: Single-quote the filter, escape inner double quotes: `jq '.["foo"]'`

Failure to quote properly causes shell interpretation of `$`, `*`, `[`, `]`, etc.
