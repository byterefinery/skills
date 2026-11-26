# Theme, sources, and v3 compatibility

## @theme

Define the design system as custom properties. A `@theme` block may only contain custom properties or `@keyframes` — anything else (e.g. a nested selector) is a compile error.

```css
@theme {
  --color-primary: oklch(0.6 0.2 250);
  --font-display: "Sora", sans-serif;
  --breakpoint-lg: 64rem;

  @keyframes wobble {
    0%, 100% { transform: rotate(-3deg); }
    50% { transform: rotate(3deg); }
  }
  --animate-wobble: wobble 1s ease-in-out infinite;
}
```

Options after `@theme` (space-separated, parsed from `parseThemeOptions` in the compiler):

- `default` — values act as defaults that user `@theme` blocks can override. This is how Tailwind's own `theme.css` is declared (`@theme default { … }`), including its deprecated block `@theme default inline reference { … }`.
- `reference` — the theme is registered without emitting CSS (pair with `@reference` imports so utilities can be `@apply`ed elsewhere).
- `inline` — theme values are inlined into generated CSS instead of referencing the custom property.
- `static` — theme values are always emitted, even when no utility references them.
- `prefix(name)` — namespace prefix for the block.

The emitted variables are plain CSS custom properties (e.g. `--color-black` resolves in generated CSS as `var(--color-black)`), so utilities stay dynamic and can be overridden in CSS.

## Default theme namespaces (from packages/tailwindcss/theme.css)

Colors — each in 50–950 steps, OKLCH values: red, orange, amber, yellow, lime, green, emerald, teal, cyan, sky, blue, indigo, violet, purple, fuchsia, pink, rose, slate, gray, zinc, neutral, stone, plus mauve, olive, mist, taupe; `--color-black`, `--color-white`.

Other namespaces:

```css
--spacing: 0.25rem;                       /* multiplier used by m-*, p-*, gap-*, … */

--breakpoint-sm: 40rem;  --breakpoint-md: 48rem;  --breakpoint-lg: 64rem;
--breakpoint-xl: 80rem;  --breakpoint-2xl: 96rem;

--container-3xs: 16rem; … --container-7xl: 80rem;   /* max-w-3xs … max-w-7xl */

--text-xs: 0.75rem; … --text-9xl: 8rem;
--text-xs--line-height: calc(1 / 0.75); …            /* sub-key pairs with --text-* */

--font-sans / --font-serif / --font-mono;
--font-weight-thin: 100; … --font-weight-black: 900;
--tracking-tighter … --tracking-widest;
--leading-tight … --leading-loose;
--radius-xs … --radius-4xl;
--shadow-2xs … --shadow-2xl;  --inset-shadow-2xs … ;  --drop-shadow-xs … ;  --text-shadow-2xs … ;
--ease-in / --ease-out / --ease-in-out;
--animate-spin / --animate-ping / --animate-pulse / --animate-bounce;  /* + @keyframes */
--blur-xs … --blur-3xl;
--perspective-dramatic: 100px; … --perspective-distant: 1200px;
--aspect-video: 16 / 9;
--default-transition-duration: 150ms;
--default-transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
--default-font-family / --default-font-feature-settings / --default-font-variation-settings;
--default-mono-font-family / …;
```

Notes:

- Utility lookup for sizing goes through several namespaces — e.g. width resolves `--width-*`, then the `--spacing` multiplier, then `--container-*` (per the `w` utility registration).
- Sub-keys use the `--` separator: `--text-lg--line-height` is the line height for `text-lg`; `--font-sans--font-feature-settings` pairs with `--font-sans`.

## @source

Control what the scanner reads. Paths must be quoted.

```css
@source "./src/**/*.{ts,tsx}";      /* add a source glob */
@source not "./legacy/**/*";        /* exclude */
@source inline("underline");        /* always emit these candidates (brace expansion works) */
@source not inline("debug-*");      /* never emit these */
```

The scan root itself can be set or disabled via parameters on `@tailwind utilities`:

```css
@tailwind utilities source('…');   /* explicit root (must be a directory) */
@tailwind utilities source(none);  /* disable automatic source detection */
```

Without any `@source`, the scanner auto-detects sources from the project (root-level patterns), and automatic detection respects `.gitignore` including negation patterns (`/*` + `!/…`).

## @reference

```css
@reference './components.css';
```

Imports a stylesheet in reference mode — its theme, utilities, variants, and plugins are registered but no CSS is emitted from the import. Used to `@apply` utilities defined in another file:

```css
@reference './foo/bar.css';

.bar {
  @apply md:hocus:foo;   /* works: the imported @utility foo and @custom-variant hocus are available */
}
```

## v3 compatibility — @config and @plugin

```css
@config "../tailwind.config.js";

@plugin "./plugins/fancy.js";
@plugin "./plugins/other.js" {
  option: value;          /* flat declarations: strings, numbers, booleans, comma lists */
}
```

- `@config` cannot be nested and cannot have a body.
- `@plugin` cannot be nested; options must be a flat list of declarations — object values are rejected (use a JS config file for those).
- The v3 JS plugin API works unchanged through `tailwindcss/plugin`:

```js
import plugin from 'tailwindcss/plugin'

export default plugin(function ({
  addBase,
  addVariant,
  matchVariant,
  addUtilities,
  matchUtilities,
  addComponents,
  matchComponents,
  theme,
  config,
  prefix,
}) {
  matchUtilities(
    {
      background: (value) => ({ background: value }),
    },
    { type: ['color', 'image'] },
  )
})

// Options-supporting plugin:
export default plugin.withOptions(
  (options) => function ({ addUtilities }) { /* … */ },
  (options) => ({ theme: { /* … */ } }),
)
```

`matchVariant(name, cb(value, { modifier }), { values, sort })`, `matchUtilities(utilities, { type, supportsNegativeValues, values (incl. __BARE_VALUE__), modifiers })`, `theme(path, defaultValue)`, `config(path, defaultValue)`, and `prefix(className)` are the full `PluginAPI` surface (from `compat/plugin-api.ts`).

## CSS value functions

`theme(…)` resolves theme values inside CSS (with the v3 dotted-key compat, e.g. `theme(colors.red.500/50%)`). Custom utility values use `--value(…)` / `--default(…)` (see [03-directives](03-directives.md)). Inline `theme(…)` alphas from v3 configs migrate to percentage modifiers (4.3.4/4.3.5 canonicalization fixes).
