# @-Directives

Tailwind CSS v4 introduces several CSS-native directives for customization.

## @import

Import Tailwind and use CSS functions:

```css
@import "tailwindcss";
```

Import specific parts:

```css
@import "tailwindcss/theme";
@import "tailwindcss/utilities";
```

Import with Tailwind functions:

```css
@import url("https://example.com/fonts.css") layer(vendor);
```

## @layer

Organize CSS into layers for cascade control. Four built-in layers:

1. `theme` — `@theme` blocks
2. `base` — preflight and base styles
3. `components` — component classes
4. `utilities` — utility classes

```css
@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium;
  }
}

@layer utilities {
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
}
```

Layer order: `theme` < `base` < `components` < `utilities`. Later layers override earlier ones.

## @theme

Define design tokens as CSS custom properties. Values are automatically available in utilities.

```css
@theme {
  --color-brand: oklch(0.7 0.15 145);
  --font-heading: "Inter", sans-serif;
  --breakpoint-3xl: 120rem;
}
```

### Theme Options

**default** — user values can override:

```css
@theme default {
  --spacing: 0.25rem;
}
```

**inline** — inline values into utilities instead of using `var()`:

```css
@theme inline {
  --spacing: 0.25rem;
}
```

**reference** — define tokens for use in other theme values but don't emit CSS:

```css
@theme reference {
  --color-internal: red;
}
```

Combined:

```css
@theme default inline {
  --spacing: 0.25rem;
}
```

### Namespace Clearing

Remove all values in a namespace:

```css
@theme {
  --color-red-*: initial;
  --color-blue-*: initial;
}
```

Clear all theme values:

```css
@theme {
  --*: initial;
}
```

## @apply

Apply utility classes inside CSS rules. Only works with standard utilities (not arbitrary values).

```css
.btn {
  @apply px-4 py-2 bg-blue-500 text-white rounded-lg;
  @apply hover:bg-blue-600 focus:ring-2 focus:ring-blue-300;
}
```

Cannot be used inside `@keyframes`. Can be used inside `@utility`.

## @utility

Define custom utility classes.

### Static Utilities

```css
@utility scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
```

Usage: `<div class="scrollbar-hide">`.

### Functional Utilities

Use `-*` suffix and `--value()` function:

```css
@utility tab-* {
  tab-size: --value(integer);
}
```

Usage: `<div class="tab-4">`, `<div class="tab-8">`.

### Value Types

```css
@utility letter-spacing-* {
  letter-spacing: --value(length);
}

@utility opacity-* {
  opacity: calc(--value(percentage) / 100);
}

@utility z-* {
  z-index: --value(integer);
}

@utility aspect-* {
  aspect-ratio: --value(ratio);
}
```

### Theme Values in Utilities

```css
@utility text-* {
  font-size: --value(--text-*--line-height);
}

@utility bg-* {
  background-color: --value(--color);
}
```

### Default Values

```css
@utility shadow {
  box-shadow: --default(0 1px 3px rgb(0 0 0 / 0.1));
}
```

### Arbitrary Values

```css
@utility transform-* {
  transform: --value([*]);
}
```

Usage: `<div class="transform-[rotate(45deg)]">`.

### Modifiers

```css
@utility text-* {
  font-size: --value(--text);
  line-height: --modifier(--leading);
}
```

Usage: `<div class="text-lg/8">`.

### Literal Values

```css
@utility cursor-* {
  cursor: --value('grab', 'grabbing', 'pointer');
}
```

Usage: `<div class="cursor-grab">`.

### Complex Example

```css
@utility spacing-* {
  --spacing-value: --value(--spacing, number);
  padding: calc(var(--spacing-value) * var(--spacing));
}
```

## @variant

Define custom variants.

### Selector Variants

```css
@variant highlighted {
  &:is(.highlighted, .highlighted *) {
    @slot;
  }
}
```

Usage: `<div class="highlighted:bg-yellow-100">`.

### At-Rule Variants

```css
@variant prefers-reduced-motion {
  @media (prefers-reduced-motion: reduce) {
    @slot;
  }
}
```

### Compound Variants

```css
@variant sidebar {
  &:is(.sidebar &, .sidebar &:hover) {
    @slot;
  }
}
```

### @slot

`@slot` is replaced with the utility's CSS rules inside `@variant` blocks.

```css
@variant my-variant {
  &.my-selector {
    @slot;
  }
}
```

## @source

Specify additional directories to scan for class names:

```css
@source "../components";
@source "../templates";
```

## @custom-variant / @custom-utility

Alias for `@variant` / `@utility` (legacy naming).

## @debug

Log information during build:

```css
@debug;  /* logs all candidates found */
```
