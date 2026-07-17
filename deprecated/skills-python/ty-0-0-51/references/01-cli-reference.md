# CLI Reference

## Commands

### `ty check`

Check a project for type errors. Scans all Python files in the working directory or project root by default.

```
ty check [OPTIONS] [PATH]...
```

**Arguments:**
- `PATH...` — Files or directories to check. Default: project root.

**Options:**

| Flag | Description |
|------|-------------|
| `--add-ignore` | Add `ty: ignore` comments to suppress all rule diagnostics |
| `--color auto\|always\|never` | Control colored output |
| `-c, --config <key=value>` | Override a specific config option (TOML pair) |
| `--config-file <path>` | Path to a `ty.toml` file (not `pyproject.toml`) |
| `--error <rule>` | Treat rule as error severity (repeatable, use `all` for all rules) |
| `--error-on-warning` | Exit 1 if any warning-level diagnostics exist |
| `--exclude <pattern>` | Gitignore-style glob to exclude files |
| `--exit-zero` | Always exit 0 even with errors |
| `--extra-search-path <path>` | Additional module resolution path (repeatable) |
| `--fix` | Apply fixes to resolve errors |
| `--force-exclude` | Enforce exclusions even for explicit paths |
| `--ignore <rule>` | Disable a rule (repeatable, use `all` for all rules) |
| `--no-progress` | Hide spinners and progress bars |
| `--output-format` | Output format: `full`, `concise`, `gitlab`, `github`, `junit` |
| `--project <dir>` | Run within a specific project directory |
| `-p, --python, --venv <path>` | Path to Python interpreter or venv |
| `--python-platform <platform>` | Target platform: `win32`, `darwin`, `linux`, `android`, `ios`, `all` |
| `--python-version <version>` | Target Python version: 3.7 through 3.15 |
| `-q, --quiet` | Quiet output (`-qq` for silent) |
| `--respect-ignore-files` | Respect `.gitignore` exclusions (default enabled) |
| `--typeshed <path>` | Custom typeshed directory for stdlib stubs |
| `-v, --verbose` | Verbose output (`-vv`, `-vvv` for more) |
| `--warn <rule>` | Treat rule as warning severity (repeatable, use `all` for all rules) |
| `-W, --watch` | Watch mode — recheck on file changes with fine-grained incrementality |

### `ty server`

Start the language server protocol (LSP) server for editor integration.

```
ty server
```

No additional options. Connect your editor's LSP client to this process.

### `ty version`

Display ty version information.

```
ty version [--output-format text|json]
```

### `ty explain rule [RULE]`

Explain a rule (or all rules if omitted).

```
ty explain rule [--output-format text|json] [RULE]
```

### `ty generate-shell-completion <SHELL>`

Generate shell autocompletion scripts for `bash`, `zsh`, `fish`, `elvish`, or `powershell`.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | No error-level violations found |
| `1` | Error-level violations found (or warnings with `--error-on-warning`) |
| `2` | Invalid CLI options, config errors, or IO errors |
| `101` | Internal error |
