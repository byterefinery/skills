# Theme System

The theme system in Tailwind CSS v4 is CSS-native. Define all design tokens as CSS custom properties inside `@theme` blocks. No `tailwind.config.js` needed.

## @theme Block

```css
@theme {
  --color-brand: oklch(0.7 0.15 145);
  --color-brand-foreground: oklch(0.2 0.02 145);
  --font-heading: "Inter", sans-serif;
  --spacing-10: 2.5rem;
  --breakpoint-3xl: 120rem;
}
```

Theme values are automatically available as utility class values. `--color-brand` enables `bg-brand`, `text-brand`, `border-brand`, etc.

## Namespace Conventions

Each CSS variable prefix maps to specific utility categories:

| Prefix | Utility Category | Example |
|---|---|---|
| `--color-*` | All color utilities | `--color-brand` → `bg-brand`, `text-brand` |
| `--background-color-*` | Background color only | `--background-card` → `bg-card` |
| `--text-color-*` | Text color only | `--text-muted` → `text-muted` |
| `--border-color-*` | Border color only | `--border-subtle` → `border-subtle` |
| `--font-*` | Font family | `--font-heading` → `font-heading` |
| `--font-weight-*` | Font weight | `--font-bold: 700` → `font-bold` (override) |
| `--text-*` | Font size (+ line-height) | `--text-xl: 1.25rem` → `text-xl` |
| `--spacing-*` | Spacing scale | `--spacing-10: 2.5rem` → `p-10`, `m-10` |
| `--breakpoint-*` | Breakpoints | `--breakpoint-3xl: 120rem` → `3xl:` |
| `--radius-*` | Border radius | `--radius-xl: 1rem` → `rounded-xl` |
| `--shadow-*` | Box shadows | `--shadow-lg` → `shadow-lg` |
| `--blur-*` | Blur filters | `--blur-md: 12px` → `blur-md` |
| `--container-*` | Container max-widths | `--container-4xl: 56rem` → `max-w-4xl` |
| `--animate-*` | Animations | `--animate-spin` → `animate-spin` |
| `--ease-*` | Easing functions | `--ease-in-out` → `ease-in-out` |
| `--z-index-*` | Z-index values | `--z-index-50: 50` → `z-50` |
| `--aspect-*` | Aspect ratios | `--aspect-video: 16/9` → `aspect-video` |
| `--scale-*` | Scale transforms | `--scale-110: 110%` → `scale-110` |
| `--rotate-*` | Rotate transforms | `--rotate-45: 45deg` → `rotate-45` |
| `--skew-*` | Skew transforms | `--skew-3: 3deg` → `skew-3` |
| `--perspective-*` | Perspective | `--perspective-dramatic: 100px` |
| `--opacity-*` | Opacity values | `--opacity-75: 75%` → `opacity-75` |
| `--tracking-*` | Letter spacing | `--tracking-wide: 0.025em` → `tracking-wide` |
| `--leading-*` | Line height | `--leading-relaxed: 1.625` → `leading-relaxed` |
| `--gap-*` | Gap values | `--gap-4: 1rem` → `gap-4` |
| `--flex-basis-*` | Flex basis | `--basis-full: 100%` → `basis-full` |
| `--stroke-width-*` | SVG stroke width | `--stroke-2: 2` → `stroke-2` |
| `--scroll-margin-*` | Scroll margin | `--scroll-m-4: 1rem` → `scroll-m-4` |
| `--scroll-padding-*` | Scroll padding | `--scroll-p-4: 1rem` → `scroll-p-4` |
| `--transition-delay-*` | Transition delay | `--delay-150: 150ms` → `delay-150` |
| `--transition-duration-*` | Transition duration | `--duration-300: 300ms` → `duration-300` |
| `--grid-column-*` | Grid column | `--col-1: 1` → `col-1` |
| `--grid-row-*` | Grid row | `--row-1: 1` → `row-1` |
| `--inset-*` | Inset values | `--inset-0: 0` → `inset-0` |
| `--margin-*` | Margin values | `--margin-auto: auto` → `m-auto` |
| `--padding-*` | Padding values | `--padding-4: 1rem` → `p-4` |
| `--width-*` | Width values | `--width-screen: 100vw` → `w-screen` |
| `--min-width-*` | Min width | `--min-w-0: 0` → `min-w-0` |
| `--max-width-*` | Max width | `--max-w-prose: 65ch` → `max-w-prose` |
| `--height-*` | Height values | `--height-screen: 100vh` → `h-screen` |
| `--min-height-*` | Min height | `--min-h-0: 0` → `min-h-0` |
| `--max-height-*` | Max height | `--max-h-screen: 100vh` → `max-h-screen` |
| `--cursor-*` | Cursor | `--cursor-grab: grab` → `cursor-grab` |
| `--columns-*` | Columns | `--columns-3: 3` → `columns-3` |
| `--line-clamp-*` | Line clamp | `--line-clamp-3: 3` → `line-clamp-3` |
| `--list-style-type-*` | List style | `--list-disc: disc` → `list-disc` |
| `--accent-color-*` | Accent color | `--accent-brand: var(--color-brand)` → `accent-brand` |
| `--caret-color-*` | Caret color | `--caret-brand: var(--color-brand)` → `caret-brand` |
| `--divide-color-*` | Divide color | `--divide-gray: var(--color-gray-200)` → `divide-gray` |
| `--divide-width-*` | Divide width | `--divide-2: 2px` → `divide-2` |
| `--fill-*` | SVG fill | `--fill-brand: var(--color-brand)` → `fill-brand` |
| `--gradient-color-stop-positions-*` | Gradient stops | `--gradient-25: 25%` → `from-25%` |
| `--stroke-*` | SVG stroke | `--stroke-brand: var(--color-brand)` → `stroke-brand` |
| `--scrollbar-*` | Scrollbar | `--scrollbar-thumb: gray` → `scrollbar-thumb-gray` |
| `--drop-shadow-*` | Drop shadow | `--drop-shadow-md` → `drop-shadow-md` |
| `--text-shadow-*` | Text shadow | `--text-shadow-sm` → `text-shadow-sm` |
| `--box-shadow-color-*` | Shadow color | `--shadow-brand: var(--color-brand)` → `shadow-brand` |
| `--ring-color-*` | Ring color | `--ring-brand: var(--color-brand)` → `ring-brand` |
| `--ring-width-*` | Ring width | `--ring-2: 2px` → `ring-2` |
| `--ring-offset-width-*` | Ring offset | `--ring-offset-2: 2px` → `ring-offset-2` |
| `--outline-color-*` | Outline color | `--outline-brand: var(--color-brand)` → `outline-brand` |
| `--outline-width-*` | Outline width | `--outline-2: 2px` → `outline-2` |
| `--outline-offset-*` | Outline offset | `--outline-offset-2: 2px` → `outline-offset-2` |
| `--text-decoration-thickness-*` | Decoration thickness | `--decoration-2: 2px` → `decoration-2` |
| `--text-decoration-color-*` | Decoration color | `--decoration-brand` → `decoration-brand` |
| `--text-underline-offset-*` | Underline offset | `--underline-offset-2: 2px` → `underline-offset-2` |
| `--placeholder-color-*` | Placeholder color | `--placeholder-gray` → `placeholder-gray` |
| `--brightness-*` | Brightness filter | `--brightness-50: 50%` → `brightness-50` |
| `--contrast-*` | Contrast filter | `--contrast-200: 200%` → `contrast-200` |
| `--grayscale-*` | Grayscale filter | `--grayscale-100: 100%` → `grayscale-100` |
| `--hue-rotate-*` | Hue rotate filter | `--hue-rotate-15: 15deg` → `hue-rotate-15` |
| `--invert-*` | Invert filter | `--invert-100: 100%` → `invert-100` |
| `--saturate-*` | Saturate filter | `--saturate-200: 200%` → `saturate-200` |
| `--sepia-*` | Sepia filter | `--sepia-100: 100%` → `sepia-100` |
| `--backdrop-blur-*` | Backdrop blur | `--backdrop-blur-md: 12px` → `backdrop-blur-md` |
| `--backdrop-brightness-*` | Backdrop brightness | `--backdrop-brightness-50: 50%` → `backdrop-brightness-50` |
| `--backdrop-contrast-*` | Backdrop contrast | `--backdrop-contrast-200: 200%` → `backdrop-contrast-200` |
| `--backdrop-grayscale-*` | Backdrop grayscale | `--backdrop-grayscale-100: 100%` → `backdrop-grayscale-100` |
| `--backdrop-hue-rotate-*` | Backdrop hue rotate | `--backdrop-hue-rotate-15: 15deg` → `backdrop-hue-rotate-15` |
| `--backdrop-invert-*` | Backdrop invert | `--backdrop-invert-100: 100%` → `backdrop-invert-100` |
| `--backdrop-opacity-*` | Backdrop opacity | `--backdrop-opacity-50: 50%` → `backdrop-opacity-50` |
| `--backdrop-saturate-*` | Backdrop saturate | `--backdrop-saturate-200: 200%` → `backdrop-saturate-200` |
| `--backdrop-sepia-*` | Backdrop sepia | `--backdrop-sepia-100: 100%` → `backdrop-sepia-100` |

## Default Theme Values

The default theme includes:

**Colors** — 20 palettes (red, orange, amber, yellow, lime, green, emerald, teal, cyan, sky, blue, indigo, violet, purple, fuchsia, pink, rose, slate, gray, zinc, neutral, stone) plus mauve, olive, mist, taupe. Each with 11 shades (50–950). All in oklch format.

**Spacing** — Base `0.25rem`. Scale: `0`, `0.5`, `1`, `1.5`, `2`, `2.5`, `3`, `3.5`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`, `14`, `16`, `20`, `24`, `28`, `32`, `36`, `40`, `44`, `48`, `52`, `56`, `60`, `64`, `72`, `80`, `96`.

**Breakpoints** — `sm: 40rem`, `md: 48rem`, `lg: 64rem`, `xl: 80rem`, `2xl: 96rem`.

**Font sizes** — `xs` (0.75rem) through `9xl` (8rem), each with computed line-height.

**Font weights** — `thin` (100), `extralight` (200), `light` (300), `normal` (400), `medium` (500), `semibold` (600), `bold` (700), `extrabold` (800), `black` (900).

**Border radius** — `xs` (0.125rem) through `4xl` (2rem).

**Shadows** — `2xs`, `xs`, `sm`, `md`, `lg`, `xl`, `2xl`. Plus `inset-shadow-*` and `drop-shadow-*`.

**Blur** — `xs` (4px) through `3xl` (64px).

**Animations** — `spin`, `ping`, `pulse`, `bounce` with built-in keyframes.

**Easing** — `in`, `out`, `in-out`.

## Advanced Theme Patterns

### Font with line-height and letter-spacing

```css
@theme {
  --text-heading: 2.25rem;
  --text-heading--line-height: 2.5 / 2.25;
  --text-heading--letter-spacing: -0.025em;
  --text-heading--font-weight: 700;
}
```

`text-heading` now sets font-size, line-height, letter-spacing, and font-weight together.

### Custom color with multiple shades

```css
@theme {
  --color-brand-50: oklch(0.97 0.01 145);
  --color-brand-100: oklch(0.94 0.02 145);
  --color-brand-500: oklch(0.7 0.15 145);
  --color-brand-900: oklch(0.25 0.08 145);
}
```

Enables `bg-brand-50`, `text-brand-500`, `border-brand-900`, etc.

### Overriding defaults

```css
@theme {
  --color-red-500: oklch(0.6 0.25 25);  /* override default */
  --spacing-10: 2.75rem;  /* override default */
}
```

### Removing defaults

```css
@theme {
  --color-red-*: initial;  /* remove all red shades */
  --color-blue-*: initial;  /* remove all blue shades */
}
```

### Reference mode (no CSS output)

```css
@theme reference {
  --color-internal: red;  /* available for utilities but not emitted */
}
```

Use for internal tokens that should not appear in the final CSS but can be referenced by other theme values.

### Default inline theme

```css
@theme default inline {
  --spacing: 0.25rem;  /* inline the value into utilities */
}
```

`default` means user values can override it. `inline` means the value is inlined rather than using `var()`.

## Theme Functions

### --theme()

Reference theme values in CSS:

```css
.card {
  background: --theme(--color-brand-500);
  padding: --theme(--spacing-4);
}
```

With fallback:

```css
.card {
  color: --theme(--color-brand, blue);
}
```

Force inline resolution:

```css
.card {
  background: --theme(--color-brand-500 inline);
}
```

### --spacing()

Multiply by the spacing base:

```css
.card {
  padding: --spacing(4);  /* 4 * 0.25rem = 1rem */
  margin: --spacing(1.5);  /* 1.5 * 0.25rem = 0.375rem */
}
```

### --alpha()

Apply opacity to a color:

```css
.card {
  background: --alpha(var(--color-brand) / 50%);
}
```

## Preflight

Tailwind v4 includes a modern reset (preflight) covering:

- `box-sizing: border-box` on all elements
- Default margins and padding removed
- Consistent font inheritance on form elements
- `img`, `svg`, `video` set to `display: block`
- `table` border collapse and text indent reset
- List styles removed from `ol`, `ul`, `menu`
- `[hidden]` elements hidden (except `[hidden="until-found"]`)

Preflight is imported automatically with `@import "tailwindcss"`. To disable:

```css
@import "tailwindcss/utilities";  /* utilities only, no preflight */
```
