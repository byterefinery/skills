# Custom CSS directives

## @utility

Define custom utilities in CSS. Static and functional forms:

```css
/* Static utility */
@utility badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: calc(var(--radius) * 1.5);
}

/* Functional utility — name must end in -*, dynamic part appears once at the end */
@utility push-* {
  right: --value(--spacing);
}

/* Functional utility with a default value */
@utility push-* {
  right: --default(1rem, --value(--spacing));
}
```

Rules enforced by the compiler:

- Must be top-level — `@utility cannot be nested`.
- Must have at least one property — `@utility … is empty` otherwise.
- Names are alphanumeric starting with a lowercase letter; escapes work (`@utility push-1\/2`, `@utility push-50\%`).
- A functional utility must end in `-*`; the dynamic `-*` may only appear once, at the end.
- `--value(…)` resolves the candidate's value (optionally typed by a theme namespace, e.g. `--value(--color-*)`); `--default(…)` supplies the fallback. Whitespace inside `--default(…)` values is preserved (fixed in 4.3.4).
- Utilities can `@apply` other utilities (defined in the same file, in any order), including with variants — circular application is an error.

Example from the test suite (functional utility with nested rules):

```css
@utility bg-* {
  & > * {
    --nearest-bg: --value(--color-*);
  }
}
```

## @custom-variant

Register a new variant. Either a selector list (body-less) or a body with `@slot` — never both, and never nested.

```css
/* Body-less, multiple selectors */
@custom-variant hocus (&:hover, &:focus);

/* At-rule condition as a selector */
@custom-variant any-hover (@media (any-hover: hover));

/* & is substituted with the utility selector (vendor functions work) */
@custom-variant firefox (:-moz-any(&));

/* Body form — @slot marks where the utility lands */
@custom-variant hocus {
  &:hover { @slot; }
  &:focus { @slot; }
}
```

Name rules: alphanumeric, dashes or underscores, starting with a lowercase letter or number; no colons; not a bare dash/underscore.

Typical class-based dark mode (the built-in `dark:` is `prefers-color-scheme`):

```css
@custom-variant dark (&:where(.dark, .dark *));
```

## @variant (styling directive)

Apply an existing variant to plain CSS rules — the styling counterpart of a variant prefix:

```css
.btn {
  background: black;

  @variant dark {
    background: white;
  }
}

/* Nesting and stacking work */
@variant hover {
  @variant landscape {
    .btn2 { color: red; }
  }
}
```

Legacy forms are still accepted and converted to `@custom-variant`: a body-less `@variant name (…);` and any `@variant` whose body uses `@slot`.

## @apply

Use utilities inside ordinary CSS:

```css
.button {
  @apply rounded-lg bg-blue-500 px-4 py-2 text-white;
}

/* Variants work in the chain, including custom ones (after @reference) */
.bar {
  @apply md:hocus:foo;
}
```

Constraints:

- `@apply` of a candidate that isn't a known utility is an error; a candidate that would create a circular dependency (a utility applying the very utility being defined) is also an error.
- Utilities from other stylesheets require `@reference` (see [02-theme-and-sources](02-theme-and-sources.md)).

## @scope

CSS-native `@scope` is supported and participates in compilation — variant-generated `@scope` rules wrap (rather than nest into) generated utilities, nested `@scope` rules keep their scoping semantics when flattened, and declarations directly inside `@scope` are preserved by wrapping them in `(:where(:scope))` (4.3.4 fixes).

## @tailwind utilities (v3 compatibility)

```css
@layer utilities {
  @tailwind utilities;
}
```

Replaced with the generated utility classes. Only one occurrence is processed (later ones are removed). It accepts `source(…)` / `source(none)` parameters for the scan root. `@tailwind base` and `@tailwind components` are not processed in v4.
