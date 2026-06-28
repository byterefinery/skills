# Variants

Variants are modifiers that apply utilities conditionally. They prefix utility classes with `variant:` syntax.

## State Variants

### Hover

`hover:` — applies on hover. Includes `@media (hover: hover)` guard.

```html
<button class="bg-blue-500 hover:bg-blue-600">
```

### Focus

`focus:` — applies when element is focused.

`focus-visible:` — applies on visible focus (keyboard navigation).

`focus-within:` — applies when any descendant is focused.

```html
<input class="border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500">
```

### Active

`active:` — applies while element is being activated (mouse down).

```html
<button class="active:scale-95">
```

### Visited

`visited:` — applies to visited links.

```html
<a class="text-blue-500 visited:text-purple-500">
```

### Target

`target:` — applies when element is the target of a fragment URL.

### Open

`open:` — applies to open details/popover elements.

## Form State Variants

`default:` — `:default` pseudo-class.

`checked:` — `:checked` pseudo-class.

`indeterminate:` — `:indeterminate` pseudo-class.

`placeholder-shown:` — `:placeholder-shown` pseudo-class.

`autofill:` — `:autofill` pseudo-class.

`optional:` — `:optional` pseudo-class.

`required:` — `:required` pseudo-class.

`valid:` / `invalid:` — validation states.

`user-valid:` / `user-invalid:` — user interaction validation states.

`in-range:` / `out-of-range:` — range validation.

`read-only:` — `:read-only` pseudo-class.

```html
<input class="border-gray-300 valid:border-green-500 invalid:border-red-500">
```

## Content State

`empty:` — `:empty` pseudo-class.

`enabled:` / `disabled:` — form element states.

`inert:` — `[inert]` attribute.

## Group & Peer Variants

### Group

Add `group` class to a parent. Use `group-*:` prefix on children.

```html
<div class="group">
  <h3 class="text-gray-600 group-hover:text-blue-500">Hover me</h3>
</div>
```

Named groups with modifiers: `group/name` on parent, `group-name/*:` on children.

```html
<div class="group/primary">
  <span class="group-primary-hover:text-red-500">Styled when primary group hovers</span>
</div>
```

Group compounds automatically with all other variants: `group-hover:`, `group-focus:`, `group-active:`, `group-disabled:`, etc.

### Peer

Add `peer` class to an element. Use `peer-*:` prefix on sibling elements that follow.

```html
<input class="peer border-2 focus:border-blue-500">
<label class="peer-valid:text-green-500 peer-invalid:text-red-500">Label</label>
```

Named peers: `peer/name` on element, `peer-name/*:` on siblings.

Peer compounds: `peer-hover:`, `peer-focus:`, `peer-checked:`, `peer-valid:`, etc.

## Compound Variants

### Has

`has-*:` — applies when the element has a matching descendant. Uses `:has()`.

```html
<div class="has-[input:checked]:bg-green-50">
  <input type="checkbox">
</div>
```

Compounds: `has-hover:`, `has-focus:`, `has-checked:`, etc.

### In

`in-*:` — applies when the element is inside a matching ancestor.

```html
<div class="in-hover:bg-gray-50">
  <span>Background changes when parent is hovered</span>
</div>
```

### Not

`not-*:` — negates a variant. Applies when the condition is NOT met.

```html
<div class="not-hover:opacity-100 hover:opacity-75">
```

## Universal Variants

`*:` — applies to all direct children (`:is(& > *)`).

`**:` — applies to all descendants (`:is(& *)`).

```html
<div class="*:flex **:*:text-sm">
```

## Pseudo-Element Variants

`before:`, `after:` — style `::before` and `::after` pseudo-elements.

`placeholder:` — style `::placeholder`.

`selection:` — style `::selection` and descendants' selections.

`marker:` — style `::marker` (list markers).

`backdrop:` — style `::backdrop` (modals).

`file:` — style `::file-selector-button`.

`first-letter:`, `first-line:` — style first letter/line.

`details-content:` — style `::details-content`.

```html
<div class="before:content-['→'] before:mr-2">Arrow</div>
```

## Positional Variants

`first:`, `last:`, `only:`, `odd:`, `even:`.

`first-of-type:`, `last-of-type:`, `only-of-type:`.

```html
<ul class="odd:bg-gray-50 even:bg-white">
  <li>Odd</li>
  <li>Even</li>
</ul>
```

## Responsive Variants

### Breakpoints

`sm:`, `md:`, `lg:`, `xl:`, `2xl:` — minimum width queries.

```html
<div class="hidden sm:block md:flex lg:grid">
```

### Min/Max Width

`min-*:` — minimum width. `max-*:` — maximum width.

```html
<div class="block max-md:hidden">  /* hide below md */
<div class="min-lg:flex">  /* flex above lg */
```

Arbitrary: `min-[20rem]:block`, `max-[40rem]:hidden`.

### Container Queries

`@:*` — container query (minimum width). `@min-*:`, `@max-*:`.

Named containers: `@name:*:`.

```html
<div class="@container">
  <div class="@lg:flex">  /* flex when container >= lg */
</div>
```

## Media Query Variants

### Dark Mode

`dark:` — `@media (prefers-color-scheme: dark)`.

```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
```

### Motion Preferences

`motion-safe:` — `@media (prefers-reduced-motion: no-preference)`.

`motion-reduce:` — `@media (prefers-reduced-motion: reduce)`.

### Contrast Preferences

`contrast-more:` — `@media (prefers-contrast: more)`.

`contrast-less:` — `@media (prefers-contrast: less)`.

### Orientation

`portrait:`, `landscape:`.

### Print

`print:` — `@media print`.

### Pointer

`pointer-none:`, `pointer-coarse:`, `pointer-fine:`.

`any-pointer-none:`, `any-pointer-coarse:`, `any-pointer-fine:`.

### Direction

`ltr:`, `rtl:`.

### Color

`forced-colors:` — `@media (forced-colors: active)`.

`inverted-colors:` — `@media (inverted-colors: inverted)`.

### Scripting

`noscript:` — `@media (scripting: none)`.

### Starting Style

`starting:` — `@starting-style` (for CSS transitions on appearance).

## Attribute Variants

### Aria

`aria-*:` — named aria states. `aria-[custom]:` — arbitrary.

```html
<button class="aria-expanded:bg-blue-50">
<div class="aria-[busy=true]:opacity-50">
```

Named values: `busy`, `checked`, `disabled`, `expanded`, `hidden`, `pressed`, `readonly`, `required`, `selected`.

### Data

`data-*:` — named data attributes. `data-[custom]:` — arbitrary.

```html
<div class="data-[state=open]:block data-[state=closed]:hidden">
<div class="data-[theme=dark]:bg-gray-900">
```

## Nth Child Variants

`nth-*:`, `nth-last-*:`, `nth-of-type-*:`, `nth-last-of-type-*:`.

```html
<div class="nth-2:text-lg">  /* every 2nd child */
<div class="nth-last-3:font-bold">  /* 3rd from last */
```

## Supports Variants

`supports-*:` — `@supports` queries.

```html
<div class="supports-[backdrop-filter]:backdrop-blur-md">
<div class="supports-[display:grid]:grid">
```

Shorthand: `supports-[display]` → `@supports (display: var(--tw))`.

## Variant Composition

Variants can be stacked. Order is deterministic based on variant priority.

```html
<button class="sm:hover:focus:bg-blue-600">
<div class="dark:group-hover:peer-focus:text-white">
```

## Arbitrary Variants

Use `[@selector]:` for any CSS selector.

```html
<div class="[&:nth-child(3)]:text-red-500">
<div class="[&_>img]:rounded-lg">  /* all direct child images */
<div class="[&_[data-active]]:font-bold">  /* descendants with data-active */
```

The `&` represents the element itself. Use `*` for descendants.
