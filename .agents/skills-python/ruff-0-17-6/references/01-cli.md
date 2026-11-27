# Ruff 0.17.6 — CLI reference

Contents:
- [Commands](#commands)
- [ruff check](#ruff-check)
- [ruff format](#ruff-format)
- [Global options](#global-options)
- [Environment variables](#environment-variables)
- [Argfiles](#argfiles)
- [Exit codes](#exit-codes)
- [Shell autocompletion](#shell-autocompletion)

## Commands

Top-level commands (`ruff help` lists them):

| Command | Purpose |
|---|---|
| `ruff check` | Run Ruff on the given files or directories |
| `ruff format` | Run the Ruff formatter on the given files or directories |
| `ruff rule` | Explain a rule (or all rules) |
| `ruff config` | List or describe the available configuration options |
| `ruff linter` | List all supported upstream linters |
| `ruff clean` | Clear any caches in the current directory and any subdirectories |
| `ruff server` | Run the language server |
| `ruff analyze` | Run analysis over Python source code |
| `ruff version` | Display Ruff's version |
| `ruff help` | Print help for a subcommand |

Both `check` and `format` accept `[FILES]...` (default `.`), or `-` to read from
stdin (use `--stdin-filename` to name the file).

## ruff check

```text
Usage: ruff check [OPTIONS] [FILES]...
```

Fixing:

| Flag | Meaning |
|---|---|
| `--fix` | Apply fixes to resolve lint violations (`--no-fix` to disable; combine with `--unsafe-fixes`) |
| `--unsafe-fixes` | Include fixes that may not retain the original intent of the code |
| `--show-fixes` | Show an enumeration of all fixed lint violations |
| `--diff` | Don't write fixed files; output a diff per changed file to stdout, exit 0 if no diffs. Implies `--fix-only` |
| `--fix-only` | Apply fixes but don't report on, or exit non-zero for, leftover violations. Implies `--fix` |
| `-w, --watch` | Re-run whenever files change |

Rule selection:

| Flag | Meaning |
|---|---|
| `--select <RULE_CODE>` | Comma-separated rule codes to enable (or `ALL` for all rules) — replaces config-file `select` |
| `--ignore <RULE_CODE>` | Comma-separated rule codes to disable |
| `--extend-select <RULE_CODE>` | Like `--select`, but adds codes on top of the configured rule set |
| `--per-file-ignores <PAT>` | Mappings from file pattern to codes to exclude |
| `--extend-per-file-ignores <PAT>` | Adds ignores on top of configured ones |
| `--fixable <RULE_CODE>` | Codes eligible for fix (only when fixing is enabled) |
| `--unfixable <RULE_CODE>` | Codes ineligible for fix |
| `--extend-fixable <RULE_CODE>` | Adds fixable codes on top of configured ones |

File selection:

| Flag | Meaning |
|---|---|
| `--exclude <FILE_PATTERN>` | Paths to omit from analysis |
| `--extend-exclude <FILE_PATTERN>` | Adds exclusions on top of configured ones |
| `--respect-gitignore` / `--no-respect-gitignore` | Respect `.gitignore` and other standard ignore files |
| `--force-exclude` / `--no-force-exclude` | Enforce exclusions even for paths passed directly on the CLI |

Output and misc:

| Flag | Meaning |
|---|---|
| `--output-format <F>` | `concise`, `full` (default), `json`, `json-lines`, `junit`, `grouped`, `github`, `gitlab`, `pylint`, `rdjson`, `azure`, `sarif` (env `RUFF_OUTPUT_FORMAT`) |
| `-o, --output-file <FILE>` | Write linter output to a file instead of stdout (env `RUFF_OUTPUT_FILE`) |
| `--statistics` | Show counts for every rule with at least one violation |
| `--add-noqa[=<REASON>]` | Add `noqa` directives to failing lines; optional reason appended after the codes |
| `--add-ignore[=<REASON>]` | Add `ruff: ignore` comments; in preview, uses human-readable rule names |
| `--show-files` | Show the files Ruff will run against with current settings |
| `--show-settings` | Show the settings Ruff will use to lint a given Python file |
| `--ignore-noqa` | Ignore any `# noqa` comments |
| `--target-version <V>` | `py37`…`py315` — minimum supported Python version |
| `--preview` / `--no-preview` | Enable preview mode (unstable rules and fixes) |
| `--extension <EXTENSION>` | Map file extension to language (`python`, `ipynb`, `pyi`), e.g. `--extension ipy:ipynb` |
| `-n, --no-cache` | Disable cache reads (env `RUFF_NO_CACHE`) |
| `--cache-dir <DIR>` | Cache directory (env `RUFF_CACHE_DIR`) |
| `--stdin-filename <NAME>` | File name when reading from stdin |
| `-e, --exit-zero` | Exit 0 even when violations are found |
| `--exit-non-zero-on-fix` | Exit 1 if any files were fixed, even if no violations remain |

## ruff format

```text
Usage: ruff format [OPTIONS] [FILES]...
```

| Flag | Meaning |
|---|---|
| `--check` | Don't write files; exit non-zero if any file would be modified |
| `--diff` | Don't write files; print the difference (exit non-zero on diff) |
| `--line-length <N>` | Set the line length (dedicated flag) |
| `--extension <EXTENSION>` | Map file extension to language (`python`, `ipynb`, `pyi`) |
| `--target-version <V>` | `py37`…`py315` |
| `--preview` / `--no-preview` | Enable unstable formatting |
| `--output-format <F>` | Output format when used with `--check` (same list as `check`) |
| `--respect-gitignore`, `--exclude`, `--extend-exclude`, `--force-exclude` | As in `check` |
| `-n, --no-cache`, `--cache-dir`, `--stdin-filename` | As in `check` |
| `--exit-non-zero-on-format` | Exit non-zero if any files were formatted |
| `--range <RANGE>` | Format only the given range, `<start_line>:<start_column>-<end_line>:<end_column>` (editor option; boundaries may be extended to enclose a logical line) |

## Global options

Available on all commands:

| Flag | Meaning |
|---|---|
| `--config <CONFIG_OPTION>` | Path to a TOML config file, **or** a TOML `<KEY> = <VALUE>` pair overriding a single option (e.g. `--config "line-length = 100"`, `--config "format.quote-style = 'single'"`). Linter options need the `lint.` prefix, formatter options `format.`. Takes precedence over all config files, including ones also passed via `--config`. |
| `--isolated` | Ignore all configuration files |
| `--color <WHEN>` | `auto`, `always`, `never` |
| `-v, --verbose` | Verbose logging |
| `-q, --quiet` | Print diagnostics, but nothing else |
| `-s, --silent` | Disable all logging (still exits 1 on diagnostics) |

## Environment variables

- `RUFF_OUTPUT_FORMAT` — output serialization format
- `RUFF_OUTPUT_FILE` — output file for linter results
- `RUFF_NO_CACHE` — disable cache reads
- `RUFF_CACHE_DIR` — cache directory

## Argfiles

Prefix an argument with `@` to read arguments from a file (one per line):

```console
$ ruff check @path/to/args.txt
```

If a path that includes the leading `@` exists (e.g. `@list.py`), it is treated
as a literal path instead of an argfile. Useful when the path list exceeds the
shell's command-line length limit.

## Exit codes

`ruff check`:

- `0` — no violations found, or all violations were fixed automatically
- `1` — violations found
- `2` — abnormal termination (invalid configuration, invalid CLI options, internal error)

Modified by `--exit-zero` (always 0 on violations) and `--exit-non-zero-on-fix`
(1 if anything was fixed, even if clean afterward).

`ruff format`:

- `0` — success (regardless of whether files were formatted)
- `1` — success with `--exit-non-zero-on-format` and one or more files formatted
- `2` — abnormal termination

`ruff format --check`:

- `0` — no files would be formatted
- `1` — one or more files would be formatted
- `2` — abnormal termination

Convention mirrors ESLint, Prettier, and RuboCop.

## Shell autocompletion

Generate a completion script per shell (`bash`, `elvish`, `fig`, `fish`,
`powershell`, `zsh`):

```bash
ruff generate-shell-completion bash   # or zsh, fish, elvish, powershell, fig
```
