# Suppression and Baselines (ty 0.0.111)

Source: `docs/suppression.md` in the ty repository at tag 0.0.111 (https://github.com/astral-sh/ty/tree/0.0.111).

- [ty suppression comments](#ty-suppression-comments)
- [Standard suppression comments](#standard-suppression-comments)
- [Multiple suppression comments](#multiple-suppression-comments)
- [Unused suppression comments](#unused-suppression-comments)
- [`@no_type_check`](#no_type_check-directive)
- [Baselines](#baselines) (preview)

## ty suppression comments

To suppress a rule violation inline, add a `# ty: ignore[<rule>]` comment at the end of the line:

```py
a = 10 + "test"  # ty: ignore[unsupported-operator]
```

- Multi-line violations: put the comment at the end of the violation's **first or last line**.
- Multiple violations on one line: enumerate rules separated by commas — `# ty: ignore[missing-argument, invalid-argument-type]`.
- Entire file: a `# ty: ignore[<rule>]` comment on its own line **before any Python code**.
- Enumerating rule names is optional but strongly recommended, to avoid accidentally suppressing other errors.

To disable a rule entirely (rather than at one location), set its level to `ignore` via `--ignore <rule>` or `[tool.ty.rules]`.

## Standard suppression comments

ty supports the standard `# type: ignore` comment format from PEP 484:

- `# type: ignore` suppresses **all** rule violations on that line (with a few narrow exceptions, see unused suppression comments).
- `# type: ignore[ty:<rule>]` behaves like `# ty: ignore[<rule>]` — only the matching rule is suppressed. Codes without a `ty:` prefix are ignored by ty, so one comment can carry suppressions for multiple checkers:

```python
sum_three_numbers("one", 5, 2)  # type: ignore[arg-type, ty:invalid-argument-type]
```

## Multiple suppression comments

To suppress a typing error on a line that already has a suppression comment from another tool, add the `# ty: ignore` comment to the same line:

```python
result = calculate()  # ty: ignore[invalid-argument-type]  # fmt: skip
```

## Unused suppression comments

By default, ty warns about unused suppression comments. Each comment format has its own rule, configurable independently:

- `unused-ignore-comment` — checks `# ty: ignore` comments.
- `unused-type-ignore-comment` — checks blanket `# type: ignore` comments and `ty:`-prefixed codes inside `type: ignore[...]` (ty only checks the `ty:` part; other checkers' codes are skipped).

Most rules can be suppressed by a blanket `# ty: ignore` or `# type: ignore`. The two `unused-*` rules above are exceptions, so an unused blanket comment can't silence the warning about itself. The same restriction applies to the opt-in `blanket-ignore-comment` rule (default level `ignore`), which flags `# ty: ignore` comments that omit rule names.

To keep an unused `# ty: ignore` comment, include `unused-ignore-comment` in its rule list: `# ty: ignore[invalid-assignment, unused-ignore-comment]`.

`analysis.respect-type-ignore-comments` (default `true`) can make ty treat `# type: ignore` as an ordinary comment, forcing `# ty: ignore` instead.

## `@no_type_check` directive

ty supports the `@no_type_check` decorator to suppress all violations inside a function:

```python
from typing import no_type_check

@no_type_check
def main():
    sum_three_numbers(1, 2)  # no error for the missing argument
```

Decorating a class with `@no_type_check` is not supported.

## Baselines

**Preview** — requires ty 0.0.93 or later; the file format may change during preview. If ty can't read your baseline after an upgrade, regenerate it with `--update-baseline`.

A baseline is a JSON file recording existing rule violations. On subsequent runs, `ty check` skips matching violations so you focus on those introduced by new or modified code. In the editor, matching violations still appear as hints.

### Create a baseline

From the project root:

```shell
ty check --update-baseline --baseline ty-baseline.json
```

Then use it on subsequent checks with `--baseline ty-baseline.json`, or persist it in config:

```toml
# pyproject.toml              # ty.toml
[tool.ty]                      baseline = "ty-baseline.json"
baseline = "ty-baseline.json"
```

Commit the baseline with your configuration so contributors and CI use the same file. To make GitHub collapse the baseline diff in pull requests, mark it generated in `.gitattributes`:

```gitattributes
/ty-baseline.json linguist-generated=true
```

### When to update the baseline

Update after fixing a violation or when one reappears in `ty check` output (e.g. after a file rename), or to suppress existing violations of a newly enabled rule. First run `ty check` to review new violations, then run `ty check --update-baseline` to add them and remove entries for fixed ones.

Alternative for one-shot suppression: `ty check --add-ignore` rewrites the source, adding `ty: ignore` comments for all rule diagnostics.
