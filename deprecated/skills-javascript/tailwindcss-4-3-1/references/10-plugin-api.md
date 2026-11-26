# Plugin API

Tailwind CSS v4 provides a plugin API for extending utilities, variants, and base styles. Plugins use the same API as v3 but work with the CSS-native theme system.

## Creating Plugins

```js
import plugin from 'tailwindcss/plugin'

const myPlugin = plugin(function ({ addUtilities, addVariant, matchUtilities, theme }) {
  // plugin logic
})

export default myPlugin
```

## Using Plugins

Import in your CSS:

```css
@import "tailwindcss";
@plugin "./my-plugin.js";
```

Or with options:

```css
@plugin "./my-plugin.js" {
  --custom-value: 1rem;
}
```

## addUtilities

Add static utility classes:

```js
addUtilities({
  '.scrollbar-hide': {
    '-ms-overflow-style': 'none',
    'scrollbar-width': 'none',
    '&::-webkit-scrollbar': { display: 'none' },
  },
  '.anim-pulse': {
    animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
  },
})
```

Multiple groups:

```js
addUtilities(
  [
    { '.btn': { /* ... */ } },
    { '.card': { /* ... */ } },
  ],
  { respectImportant: true }
)
```

## addComponents

Same as `addUtilities` but adds to the `components` layer instead of `utilities`:

```js
addComponents({
  '.btn-primary': {
    '@apply px-4 py-2 bg-blue-500 text-white rounded': {},
  },
})
```

## addVariant

### Static Variants

```js
addVariant('hover', '&:hover')
addVariant('checked', '&:checked')
```

Multiple selectors:

```js
addVariant('ie11', ['@supports (-ms-accelerator:true)'])
```

CSS-in-JS object:

```js
addVariant('modal', {
  '&:is(.modal &, .modal &:hover)': {},
})
```

### Functional Variants

```js
addVariant('supports', (value) => `@supports (${value})`)
```

Usage: `supports-[display:grid]:grid`.

With values:

```js
addVariant('direction', {
  values: {
    ltr: '&:where(:dir(ltr))',
    rtl: '&:where(:dir(rtl))',
  },
})
```

Usage: `direction-ltr:flex`, `direction-rtl:hidden`.

## matchUtilities

Create dynamic utilities that accept values:

```js
matchUtilities(
  {
    'text-shadow': (value) => ({
      'text-shadow': value,
    }),
  },
  {
    values: {
      sm: '0 1px 2px rgb(0 0 0 / 0.1)',
      md: '0 2px 4px rgb(0 0 0 / 0.1)',
      lg: '0 4px 8px rgb(0 0 0 / 0.1)',
    },
    type: 'color',
  }
)
```

Usage: `text-shadow-sm`, `text-shadow-lg`.

### Value Types

```js
matchUtilities(
  {
    'blur': (value) => ({ filter: `blur(${value})` }),
  },
  {
    type: 'length',  // 'length', 'color', 'number', 'percentage', 'url'
  }
)
```

### Supporting Negative Values

```js
matchUtilities(
  {
    'skew-x': (value) => ({ transform: `skewX(${value})` }),
  },
  {
    values: { '1': '1deg', '2': '2deg', '3': '3deg' },
    supportsNegativeValues: true,
    type: 'angle',
  }
)
```

Usage: `skew-x-3`, `-skew-x-3`.

### Modifiers

```js
matchUtilities(
  {
    'bg': (value, { modifier }) => ({
      'background-color': modifier
        ? `color-mix(in srgb, ${value} ${modifier}, transparent)`
        : value,
    }),
  },
  {
    values: ({ color }) => color,
    modifiers: 'any',
  }
)
```

Usage: `bg-red-500/50`.

### Bare Values

```js
matchUtilities(
  {
    'delay': (value) => ({ 'transition-delay': value }),
  },
  {
    type: 'number',
    values: {
      '__BARE_VALUE__': (value) => `${value.value}ms`,
    },
  }
)
```

Usage: `delay-150` → `transition-delay: 150ms`.

## matchComponents

Same as `matchUtilities` but adds to the `components` layer.

## addBase

Add base styles (like preflight):

```js
addBase({
  'html': {
    fontFeatureSettings: '"cv02", "cv03", "cv04", "cv11"',
  },
  'h1': {
    fontSize: '2rem',
    fontWeight: '700',
  },
})
```

## theme()

Access theme values:

```js
plugin(function ({ theme }) {
  const spacing = theme('spacing')
  const colors = theme('colors')
  const breakpoints = theme('screens')

  addUtilities({
    '.custom-padding': {
      padding: spacing['4'],
    },
  })
})
```

## config()

Access plugin configuration:

```js
plugin(function ({ config }) {
  const important = config('important', false)
})
```

## prefix()

Get the prefixed version of a class name:

```js
plugin(function ({ prefix }) {
  addUtilities({
    [`.${prefix('custom-class')}`]: {
      /* ... */
    },
  })
})
```

## Plugin with Options

```js
import plugin from 'tailwindcss/plugin'

const aspectRatios = plugin(function ({ matchUtilities }) {
  matchUtilities(
    {
      aspect: (value) => ({
        'aspect-ratio': value,
      }),
    },
    { values: {} }
  )
}, {
  theme: {
    aspectRatios: {
      'square': '1 / 1',
      'video': '16 / 9',
    },
  },
})

export default aspectRatios
```

Usage in CSS:

```css
@plugin "./aspect-ratios.js" {
  --aspect-square: 1 / 1;
  --aspect-video: 16 / 9;
}
```

## Creating a Plugin File

```js
// my-plugin.js
import plugin from 'tailwindcss/plugin'

export default plugin(function ({ addUtilities, addVariant, matchUtilities, theme }) {
  // Add utilities
  addUtilities({
    '.scrollbar-thin': {
      'scrollbar-width': 'thin',
    },
  })

  // Add variant
  addVariant('placeholder-shown', '&:placeholder-shown')

  // Match utilities
  matchUtilities(
    {
      'backdrop-blur': (value) => ({
        '-webkit-backdrop-filter': `blur(${value})`,
        'backdrop-filter': `blur(${value})`,
      }),
    },
    {
      values: theme('blur'),
    }
  )
})
```

## v3 Compat Plugin API

For migration from v3, the compat layer provides:

```js
import { createContext, resolveConfig } from 'tailwindcss'

const context = createContext([
  {
    handler: ({ addBase, addComponents, addUtilities, addVariant, matchUtilities }) => {
      // v3-compatible plugin code
    },
  },
])
```

## Best Practices

- Use `@utility` and `@variant` directives in CSS when possible (no JS needed)
- Use the JS plugin API only when you need dynamic behavior or complex logic
- Keep plugins focused on a single concern
- Use `theme()` to read theme values for consistency
- Use `matchUtilities` with `values` from `theme()` for autocomplete support
