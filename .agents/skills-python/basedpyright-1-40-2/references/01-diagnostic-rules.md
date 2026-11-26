# BasedPyright-Exclusive Diagnostic Rules

Rules that exist only in basedpyright (not plain pyright), all enabled by default in the
`recommended` mode. Each is a normal diagnostic rule — set it to `"none"` or another severity
in config, per-file comments, or `typeCheckingMode`.

## Banning Any types

- **`reportAny`** — errors on *usages* of anything typed as `Any`, whether the `Any` was
  explicit or inferred from untyped code. Pyright's `reportUnknown*` family only catches
  "unknown" (from untyped/unfollowed imports), not explicit `Any`.
  ```py
  def foo(baz: Any) -> Any:
      print(baz)  # error: reportAny
  ```
- **`reportExplicitAny`** — errors on the *annotations* that write `Any` itself.
  ```py
  def foo(baz: Any) -> Any:  # error: reportExplicitAny (on both annotations)
      print(baz)             # error: reportAny
  ```

## Import hygiene

- **`reportImplicitRelativeImport`** — bans imports that only work when a file is run as a
  script, not when imported as a module. Inside `module_name/bar.py`, `import foo` (where
  `foo` is a sibling in the same package) is wrong; use `from . import foo`.
- **`reportPrivateLocalImportUsage`** — extends pyright's `reportPrivateImportUsage` to your
  own code: importing a name from a local module that wasn't explicitly re-exported errors.
  Re-export with a redundant alias (`from .some_module import b as b`).

## Casts and overrides

- **`reportInvalidCast`** — errors on `cast()` calls where the target type does not overlap
  the source type (`cast(str, foo)` when `foo: int`). Note dict → TypedDict casts also error
  because checkers treat `TypedDict` as unrelated to `dict`.
- **`reportIncompatibleUnannotatedOverride`** — pyright only checks attribute overrides when
  the base attribute is annotated; this rule also catches unannotated bases (`value = 1`
  overridden by `value = None`). Disabled in the default "recommended" set for performance
  reasons (planned to enable later); enable explicitly if you want it.
- **`reportUnannotatedClassAttribute`** — alternative to the above: errors on any class
  attribute that could be overridden and lacks a type annotation.

## Abstract classes

- **`reportImplicitAbstractClass`** — a subclass of an abstract class that doesn't implement
  all abstract methods is itself implicitly abstract; this rule requires it to explicitly
  extend `ABC` to make that intentional (`class FooImpl(AbstractFoo, ABC)`).
- **`reportEmptyAbstractUsage`** — instantiating a class that directly extends `ABC`/uses
  `ABCMeta` but has no abstract methods is flagged as likely unintentional.
- **`reportInvalidAbstractMethod`** — `@abstractmethod` on a method of a non-abstract class
  is reported at the definition (pyright silently ignores it).

## Structure and style

- **`reportUnsafeMultipleInheritance`** — bans multiple inheritance when more than one base
  class defines `__init__`/`__new__`, since super() chains can't be statically verified.
  This lets `reportMissingSuperCall` stay lenient (only fires on classes with a base).
- **`reportUnusedParameter`** — unused function parameters as a real diagnostic (error/warning/
  hint) instead of pyright's grey-out-only behavior.
- **`reportSelfClsDefault`** — default values for `self`/`cls` are almost certainly a mistake.

## Ignore comments

- **`reportIgnoreCommentWithoutRule`** — `# pyright: ignore` without `[rule]` is an error;
  always name the rule so that if the line later produces a *different* diagnostic, it still
  surfaces instead of being silently swallowed.
