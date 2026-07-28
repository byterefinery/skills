# Suppression

## ty suppression comments

### Line-level suppression

```python
result = bad_call("x")  # ty: ignore[invalid-argument-type]
```

Multiple rules on one line:

```python
sum_three("one", 5)  # ty: ignore[missing-argument, invalid-argument-type]
```

### File-level suppression

Place before any Python code:

```python
# ty: ignore[invalid-argument-type]

sum_three(3, 2, "1")
```

### Multi-line violations

Place on the first or last line of the violation:

```python
# On the first line
sum_three(  # ty: ignore[missing-argument]
    3,
    2
)

# Or on the last line
sum_three(
    3,
    2
)  # ty: ignore[missing-argument]
```

## Standard `type: ignore` format

ty supports PEP 484 `type: ignore` comments:

```python
# Suppress all violations on this line
sum_three("one", 5)  # type: ignore

# Suppress specific ty rule
sum_three("one", 5)  # type: ignore[ty:invalid-argument-type]

# Combine mypy and ty codes
sum_three("one", 5, 2)  # type: ignore[arg-type, ty:invalid-argument-type]
```

Codes without `ty:` prefix are ignored, allowing combined suppression for multiple checkers.

## Multiple suppression comments

Add `# ty: ignore` alongside other tool comments:

```python
result = calculate()  # ty: ignore[invalid-argument-type]  # fmt: skip
result = calculate()  # fmt: off  # ty: ignore[invalid-argument-type]
```

## `@no_type_check` directive

Suppress all violations inside a function:

```python
from typing import no_type_check

@no_type_check
def main():
    sum_three(1, 2)  # no error for the missing argument
```

Decorating a class with `@no_type_check` is not supported.

## Unused suppression comments

The `unused-ignore-comment` rule reports unused `ty: ignore` and `type: ignore` comments.

```python
x = 1  # ty: ignore[invalid-assignment]  # unused-ignore-comment violation
```

### Suppression of unused-ignore-comment

`unused-ignore-comment` violations can only be suppressed with the specific rule code:

```python
x = 1  # ty: ignore[unused-ignore-comment]  # works
x = 1  # ty: ignore                          # does NOT work
x = 1  # type: ignore                        # does NOT work
```

## `--add-ignore`

Automatically add suppression comments for all violations:

```bash
ty check --add-ignore
```

This adds `# ty: ignore[rule]` comments (with space after colon) to lines with violations.

## `respect-type-ignore-comments`

Control whether `type: ignore` comments are honored:

```toml
[analysis]
respect-type-ignore-comments = false
```

When `false`, only `ty: ignore` comments suppress errors. Useful when running ty alongside other type checkers that use their own `type: ignore` codes.

## `blanket-ignore-comment` rule

The `blanket-ignore-comment` rule flags `type: ignore` without specific error codes:

```python
x = bad_call()  # type: ignore           # blanket-ignore-comment violation
x = bad_call()  # type: ignore[arg-type] # OK — specific codes provided
```

Disabled by default. Enable for stricter suppression hygiene:

```toml
[rules]
blanket-ignore-comment = "error"
```

## Best practices

1. **Always specify rule codes** — `ty: ignore[rule]` instead of bare `ty: ignore`
2. **Prefer `ty: ignore` over `type: ignore`** — more explicit and ty-specific
3. **Use `--add-ignore` sparingly** — review auto-added comments before committing
4. **Enable `unused-ignore-comment`** — catches stale suppression comments
5. **Enable `blanket-ignore-comment`** — prevents overly broad suppressions
6. **Use `@no_type_check` for legacy code** — suppress entire functions rather than many lines
