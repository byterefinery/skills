# CLI Reference (ty 0.0.111)

Source: `docs/reference/cli.md` and `docs/reference/environment.md` in the ty repository at tag 0.0.111 (https://github.com/astral-sh/ty/tree/0.0.111). The CLI reference in the docs is auto-generated from `crates/ty/src/args.rs`.

- [ty](#ty) — top level
- [ty check](#ty-check) — check a project for type errors
- [ty server](#ty-server) — start the language server
- [ty explain](#ty-explain) — explain rules
- [ty version](#ty-version)
- [ty generate-shell-completion](#ty-generate-shell-completion)
- [Exit codes](#exit-codes)
- [Environment variables](#environment-variables)

## ty

An extremely fast Python type checker.

```
ty <COMMAND>
```

Commands: `check`, `server`, `version`, `explain`, `help`.

## ty check

Check a project for type errors.

```
ty check [OPTIONS] [PATH]...
```

**Arguments**

| Argument | Description |
|---|---|
| `PATHS` | List of files or directories to check [default: the project root] |

**Options**

| Option | Description |
|---|---|
| `--add-ignore` | Adds `ty: ignore` comments to suppress all rule diagnostics |
| `--baseline <path>` | Path to a JSON diagnostic baseline (preview) |
| `--color <when>` | Control when colored output is used: `auto` (terminal, unless overridden by environment), `always`, `never` |
| `--config` / `-c <config-option>` | A TOML `<KEY> = <VALUE>` pair (such as you might find in a `ty.toml`) overriding a specific configuration option. Always takes precedence over all configuration files |
| `--config-file <path>` | The path to a `ty.toml` file to use for configuration. `pyproject.toml` is not allowed in this context. May also be set with `TY_CONFIG_FILE` |
| `--error <rule>` | Treat the given rule as having severity `error`. Repeatable. Use `all` to apply to all rules |
| `--error-on-warning` | Use exit code 1 if there are any warning-level diagnostics. Cannot be combined with `--exit-zero` or `--exit-zero-on-warning` |
| `--exclude <glob>` | Gitignore-style patterns for files to exclude from type checking (e.g. `tests/`, `*.tmp`, `**/__pycache__/**`) |
| `--exclude-scripts` | Exclude files containing PEP 723 inline script metadata unless passed explicitly. Use `--include-scripts` to disable |
| `--exit-zero` | Always use exit code 0, even when there are error-level diagnostics. Cannot be combined with `--error-on-warning` |
| `--exit-zero-on-warning` | Use exit code 0 if there are no error-level diagnostics. Cannot be combined with `--error-on-warning` |
| `--extra-search-path <path>` | Additional module-resolution source (repeatable). Advanced option for modules not installed conventionally; prefer `--python` for unusual environment locations |
| `--fix` | Apply fixes to resolve errors |
| `--force-exclude` | Enforce exclusions, even for paths passed to ty directly on the command line. Use `--no-force-exclude` to disable |
| `--help` / `-h` | Print help (summary with `-h`) |
| `--ignore <rule>` | Disables the rule. Repeatable. Use `all` to apply to all rules |
| `--no-progress` | Hide all progress outputs (spinners, progress bars) |
| `--output-format <format>` | `full` (verbose, with context and hints, default), `concise` (one per line), `gitlab` (GitLab Code Quality JSON), `github` (GitHub Actions error annotations), `junit` (JUnit XML), `sarif` (SARIF). May also be set with `TY_OUTPUT_FORMAT` |
| `--project <project>` | Run the command within the given project directory. `pyproject.toml` files and the project's `.venv` are discovered by walking up from the given directory (unless `venv-path` is set); other relative paths resolve against the cwd |
| `--python` / `--venv <path>` | Path to the project's Python environment or interpreter, used to resolve third-party imports. May be a Python interpreter (`.venv/bin/python3`), a virtual environment directory (`.venv`), or a system Python `sys.prefix` directory (`/usr`). Usually unnecessary with uv or an activated env |
| `--python-platform` / `--platform <platform>` | Target platform for resolving types; specializes `sys.platform`. `all` makes no assumptions. Unspecified: the current system's platform |
| `--python-version` / `--target-version <version>` | Python version to assume: `3.7`–`3.15`. Affects allowed syntax and stdlib/first-/third-party type definitions. Inference order when unspecified: `project.requires-python` minimum, then the activated/configured environment, then the latest stable version ty supports |
| `--quiet` / `-q` | Quiet output (`-qq` for silent) |
| `--respect-ignore-files` | Respect exclusions via `.gitignore` and other standard ignore files. Use `--no-respect-ignore-files` to disable |
| `--typeshed` / `--custom-typeshed-dir <path>` | Custom directory for stdlib typeshed stubs |
| `--update-baseline` | Create or update the configured diagnostic baseline (preview) |
| `--verbose` / `-v` | Verbose output (`-vv`, `-vvv` for more) |
| `--warn <rule>` | Treat the given rule as having severity `warn`. Repeatable. Use `all` to apply to all rules |
| `--watch` / `-W` | Watch files for changes and recheck files related to the changed files (fine-grained incrementality) |

## ty server

Start the language server. No options beyond `--help`.

## ty explain

Explain rules and other parts of ty. Subcommand: `rule`.

### ty explain rule

Explain a rule (or all rules).

```
ty explain rule [OPTIONS] [RULE]
```

- `RULE` — rule to explain; defaults to all rules if omitted
- `--output-format <format>` — `text` (default) or `json`

## ty version

Display ty's version. `--output-format`: `text` (default) or `json`.

## ty generate-shell-completion

```
ty generate-shell-completion <SHELL>
```

Example wiring (bash): `echo 'eval "$(ty generate-shell-completion bash)"' >> ~/.bashrc` (zsh/fish/elvish/powershell equivalents are in the installation docs).

## Exit codes

| Exit code | Description |
|---|---|
| `0` | no violations with severity `warning` or higher were found |
| `1` | violations with severity `warning` or higher were found |
| `2` | invalid CLI options, invalid configuration, or IO errors |
| `101` | internal error |

Modifiers: `--exit-zero` (always 0), `--error-on-warning` (1 on warnings too), `--exit-zero-on-warning` (1 only on errors). `--error-on-warning` cannot be supplied with `--exit-zero` or `--exit-zero-on-warning`.

## Environment variables

**Defined by ty**

| Variable | Effect |
|---|---|
| `TY_CONFIG_FILE` | Path to a `ty.toml` to use instead of config discovery (equivalent to `--config-file`) |
| `TY_LOG` | Log level for `--verbose` output; any `tracing_subscriber` filter. `TY_LOG=ty=debug` ≈ `-vv`; `TY_LOG=trace` enables all trace logging |
| `TY_LOG_PROFILE` | If `"1"` or `"true"`, enable flamegraph profiling (creates a `tracing.folded` file) |
| `TY_MAX_PARALLELISM` | Upper limit on parallel tasks (e.g. files checked in parallel); not a thread limit |
| `TY_OUTPUT_FORMAT` | Diagnostic output format; same values as `--output-format` |
| `TY_UV` | uv integration. `scripts`: use uv to create/update an environment for each PEP 723 script; `1`/`true`: also use uv to discover the workspace root and Python environment; `off`: disable all uv integration even when `project-manager.project`/`script` is `"uv"`. Explicit `TY_UV` takes precedence over ty configuration |

**Externally defined variables ty reads**

| Variable | Effect |
|---|---|
| `CLICOLOR` | Color in `ty check` when stdout is a terminal; `0` disables, any other non-empty value enables (even if `TERM=dumb`) |
| `CLICOLOR_FORCE` | Alias for `FORCE_COLOR` |
| `CONDA_DEFAULT_ENV` | Name of the active Conda environment |
| `CONDA_PREFIX` | Path to the active Conda or Pixi environment; if it contains no Python interpreter, ty continues searching (including the project's `.venv`). A non-empty `VIRTUAL_ENV` takes precedence |
| `FORCE_COLOR` | Any non-empty value (including `0`) forces color, including when piped; overridden by `NO_COLOR`, `--color=always/never` |
| `NO_COLOR` | Any non-empty value disables color in diagnostics, including when piped; overridden by `--color always/never` |
| `PYTHONPATH` | Adds directories to ty's module search paths (platform pathsep separated); entries that don't exist or aren't directories are ignored |
| `RAYON_NUM_THREADS` | Upper limit on parallel threads (standard Rayon variable); equivalent to `TY_MAX_PARALLELISM` |
| `TERM` | In automatic mode, color is used when stdout is a terminal unless `TERM` is exactly `dumb` |
| `VIRTUAL_ENV` | Detects an activated virtual environment |
| `XDG_CONFIG_HOME` | Path to the user-level config directory on Unix (`~/.config/ty/ty.toml` by default) |
| `_CONDA_ROOT` | Root install path of Conda |
