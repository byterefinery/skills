# Utility syntax and built-in variants

## Candidate syntax

A candidate is `[variants:]utility[modifier][!]`:

```html
<!-- stacked variants -->
<span class="hover:focus:underline">…</span>

<!-- important: v4 puts the bang at the end; the leading v3 form still parses -->
<span class="mx-4!">…</span>

<!-- opacity modifier (percentage) -->
<span class="bg-red-500/50">…</span>

<!-- arbitrary values; viewport/font-relative units like dvmin, svi, cap, rex count as lengths (4.3.4) -->
<div class="w-[37rem] text-[10dvmin]">…</div>

<!-- arbitrary properties -->
<div class="[grid-area:header]">…</div>
```

- Candidates with unbalanced brackets/parentheses are dropped (no CSS emitted).
- A modifier that would be silently ignored (e.g. `rounded-sm/[5]`, `stroke-2/50`) produces no CSS instead of silently applying.
- Invalid UTF-8 candidates are dropped during class detection.

## Spacing and sizing

- `p-4` → `calc(var(--spacing) * 4)`; the `--spacing` multiplier (default `0.25rem`) scales the whole m/p/gap/inset family.
- Width/height resolution order: `--width-*` / `--height-*` theme keys → `--spacing` multiplier → `--container-*` keys.
- Bare numeric values are accepted on spacing utilities and resolve against the multiplier.

## Built-in variants (from the compiler's variant registry)

Responsive / media (breakpoints come from `--breakpoint-*` theme keys, so custom breakpoints work automatically):

- `sm:`, `md:`, `lg:`, `xl:`, `2xl:` — `@media (width >= …)`
- `min-*:` — arbitrary minimum width (`min-[64rem]:flex` canonicalizes to the named equivalent when it matches)
- `max-*:` — `@media (width < …)`
- `portrait:`, `landscape:`, `print:`, `starting:` (wraps in `@starting-style`), `motion-safe:`, `motion-reduce:`, `ltr:`, `rtl:`
- `dark:` — `@media (prefers-color-scheme: dark)` (override with `@custom-variant` for class-based dark mode)

State:

- `hover:` — wrapped in `@media (hover: hover)` so touch devices never get hover styles
- `focus:`, `focus-visible:`, `focus-within:`, `active:`, `enabled:`, `disabled:`, `inert:`, `open:`, `visited:`, `target:`

Forms:

- `default:`, `checked:`, `indeterminate:`, `placeholder-shown:`, `autofill:`, `optional:`, `required:`, `valid:`, `invalid:`, `user-valid:`, `user-invalid:`, `in-range:`, `out-of-range:`, `read-only:`

Positional:

- `first:`, `last:`, `only:`, `odd:`, `even:`, `first-of-type:`, `last-of-type:`, `only-of-type:`

Structural (pseudo-elements):

- `before:`, `after:` (manage `content: var(--tw-content)` automatically), `placeholder:`, `backdrop:`, `file:` (`::file-selector-button`), `details-content:`
- `*:` and `**:` — target direct descendants / all descendants of the utility

Functional (value-driven):

- `data-*:` — any `data-` attribute (`data-[state=open]`, bare `data-foo` → `[data-foo]`)
- `aria-*:` — `aria-busy`, `aria-checked`, `aria-disabled`, `aria-expanded`, `aria-hidden`, `aria-pressed`, `aria-readonly`, `aria-required`, `aria-selected` (named values compile to `[aria-x="true"]`; arbitrary values allowed)
- `nth-*:`, `nth-last-*:`, `nth-of-type:`, `nth-last-of-type:` — positive integers only for bare values
- `supports-*:` — `supports-(display:block)`, `supports-[selector(…)]` and friends (raw `and`/`or`/`not` inside selectors are preserved)

Compound (one variant applied to another — e.g. `group-hover:`, `not-hover:`, `has-checked:`, `group-has-checked:`):

- `not-*:` — negates the wrapped variant (`not-hover:flex` → `.not-hover\:flex:not(:hover)`)
- `group-*:` / `peer-*:` — with optional named groups (`group-name:` / `peer-name:`, e.g. `group-has-checked/parent-name:flex`)
- `in-*:` / `has-*:` — wraps in `(:where(…)) &` / `&:has(…)` respectively; not compatible with utilities that use nested style rules (the candidate is dropped)

## Custom variants

See [03-directives](03-directives.md) for `@custom-variant` and the `@variant` styling directive.
