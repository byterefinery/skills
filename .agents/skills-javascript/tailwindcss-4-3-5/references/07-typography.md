# Typography

## Font Family

`font-*` — resolves from `--font-*` namespace. Also supports arbitrary values.

```html
<p class="font-sans">Sans-serif</p>
<p class="font-serif">Serif</p>
<p class="font-mono">Monospace</p>
<p class="font-[Inter]">Arbitrary font</p>
```

The `font-*` utility also resolves font-weight from `--font-weight-*` namespace when a weight value is given.

## Font Weight

`font-*` resolves to `--font-weight-*` when the value matches a weight.

Static weights: `thin` (100), `extralight` (200), `light` (300), `normal` (400), `medium` (500), `semibold` (600), `bold` (700), `extrabold` (800), `black` (900).

```html
<p class="font-bold">Bold</p>
<p class="font-medium">Medium</p>
<p class="font-[600]">Arbitrary weight</p>
```

## Font Size

`text-*` — resolves from `--text-*` namespace. Each size includes line-height.

Default sizes: `xs` (0.75rem), `sm` (0.875rem), `base` (1rem), `lg` (1.125rem), `xl` (1.25rem), `2xl` (1.5rem), `3xl` (1.875rem), `4xl` (2.25rem), `5xl` (3rem), `6xl` (3.75rem), `7xl` (4.5rem), `8xl` (6rem), `9xl` (8rem).

```html
<p class="text-sm">Small</p>
<p class="text-xl">Extra large</p>
<p class="text-[15px]">Arbitrary size</p>
```

### Font Size with Line-Height Modifier

```html
<p class="text-lg/8">Large with leading-8</p>
<p class="text-xl/none">XL with no leading</p>
<p class="text-base/relaxed">Base with relaxed leading</p>
```

## Font Style

`italic`, `not-italic`.

## Font Stretch

`font-stretch-*` — `normal`, `ultra-condensed`, `extra-condensed`, `condensed`, `semi-condensed`, `semi-expanded`, `expanded`, `extra-expanded`, `ultra-expanded`.

Percentages: `font-stretch-50%`, `font-stretch-75%`, `font-stretch-90%`, `font-stretch-95%`, `font-stretch-100%`, `font-stretch-105%`, `font-stretch-110%`, `font-stretch-125%`, `font-stretch-150%`, `font-stretch-200%`.

Arbitrary: `font-stretch-[75%]`.

## Font Variant Numeric

`normal-nums` — reset all font variant numeric features.

`ordinal` — ordinal numbers.

`slashed-zero` — slashed zero glyph.

`lining-nums` — uniform height numerals.

`oldstyle-nums` — varying height numerals.

`proportional-nums` — variable width numerals.

`tabular-nums` — fixed width numerals.

`diagonal-fractions` — diagonal fraction notation.

`stacked-fractions` — stacked fraction notation.

## Font Feature Settings

`font-features-*` — arbitrary values.

```html
<p class="font-features-[='kern'_on]">
```

## Text Transform

`uppercase`, `lowercase`, `capitalize`, `normal-case`.

## Text Alignment

`text-left`, `text-center`, `text-right`, `text-justify`, `text-start`, `text-end`.

## Text Indent

`indent-*` — spacing scale, negative support.

```html
<p class="indent-6">Indented paragraph</p>
```

## Vertical Alignment

`align-baseline`, `align-top`, `align-middle`, `align-bottom`, `align-text-top`, `align-text-bottom`, `align-sub`, `align-super`.

`align-*` — arbitrary values.

## Line Height (Leading)

`leading-*` — spacing scale. Static: `none` (1).

Theme: `--leading-*` namespace (`tight`, `snug`, `normal`, `relaxed`, `loose`).

```html
<p class="leading-relaxed">Relaxed line height</p>
<p class="leading-none">No line height</p>
<p class="leading-6">Line height 1.5rem</p>
```

## Letter Spacing (Tracking)

`tracking-*` — theme values (`tighter`, `tight`, `normal`, `wide`, `wider`, `widest`). Negative: `-tracking-wide`.

Arbitrary: `tracking-[0.05em]`.

## Text Color

`text-*` — resolves from `--text-color-*` and `--color-*` namespaces. Supports opacity modifiers.

```html
<span class="text-gray-500">Gray text</span>
<span class="text-blue-500/75">Blue with 75% opacity</span>
<span class="text-[#bada55]">Arbitrary color</span>
```

## Text Decoration

### Decoration Line

`underline`, `overline`, `line-through`, `no-underline`.

### Decoration Color

`decoration-*` — colors with opacity modifiers.

### Decoration Thickness

`decoration-auto`, `decoration-from-font`, `decoration-*` — theme values or bare pixel integers.

### Decoration Style

`decoration-solid`, `decoration-double`, `decoration-dotted`, `decoration-dashed`, `decoration-wavy`.

### Underline Offset

`underline-offset-auto`, `underline-offset-*` — bare pixel integers, negative support.

## Text Overflow

`truncate` — `overflow: hidden`, `text-overflow: ellipsis`, `white-space: nowrap`.

`text-ellipsis`, `text-clip`.

## Text Wrap

`text-wrap`, `text-nowrap`, `text-balance`, `text-pretty`.

`break-normal`, `break-all`, `break-keep`.

`wrap-anywhere`, `wrap-break-word`, `wrap-normal`.

## Hyphens

`hyphens-none`, `hyphens-manual`, `hyphens-auto`.

## White Space

`whitespace-normal`, `whitespace-nowrap`, `whitespace-pre`, `whitespace-pre-line`, `whitespace-pre-wrap`, `whitespace-break-spaces`.

## Line Clamp

`line-clamp-*` — bare integers. Static: `none`.

```html
<p class="line-clamp-3">Clamped to 3 lines</p>
```

## Tab Size

`tab-*` — bare integers. Suggested: `2`, `4`, `8`.

## Antialiasing

`antialiased` — `-webkit-font-smoothing: antialiased`, `-moz-osx-font-smoothing: grayscale`.

`subpixel-antialiased` — revert to auto.

## Text Shadow

`text-shadow` — default shadow from theme. `text-shadow-*` — named shadows or colors.

`text-shadow-none` — no shadow.

`text-shadow-initial` — reset.

Opacity modifier: `text-shadow-red-500/50`.

```html
<h1 class="text-shadow-sm">Small text shadow</h1>
<h1 class="text-shadow-lg/75">Large shadow at 75% opacity</h1>
```

## Placeholder

`placeholder-*` — colors with opacity modifiers. Applies to `::placeholder` pseudo-element.

```html
<input class="placeholder-gray-400" placeholder="Enter text...">
```

## List Styles

`list-inside`, `list-outside` → `list-style-position`.

`list-none`, `list-disc`, `list-decimal`, `list-*` → `list-style-type` from theme.

`list-image-none`, `list-image-*` → `list-style-image` from theme.
