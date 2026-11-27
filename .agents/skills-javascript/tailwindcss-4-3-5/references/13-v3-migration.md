# Migrating from v3

## Key Changes

1. **No `tailwind.config.js`** — use `@theme` blocks in CSS
2. **`@tailwind` directives removed** — use `@import "tailwindcss"`
3. **`prefix` config** — use `@theme prefix: tw { }`
4. **`important` config** — use `@import "tailwindcss" important;`
5. **`darkMode` config** — media query is default; use `@variant dark` for class strategy
6. **`corePlugins`** — remove utilities by setting theme to `initial`
7. **`separator`** — always `:` in v4

## Migrating Theme Config

**v3:**
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: '#ff6600',
      },
      fontFamily: {
        heading: ['Inter', 'sans-serif'],
      },
    },
  },
}
```

**v4:**
```css
@theme {
  --color-brand: #ff6600;
  --font-heading: "Inter", sans-serif;
}
```

## Migrating Plugins

**v3:**
```js
// tailwind.config.js
module.exports = {
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

**v4:**
```css
@import "tailwindcss";
@plugin "@tailwindcss/forms";
@plugin "@tailwindcss/typography";
```

## Migrating Presets

**v3:**
```js
module.exports = {
  presets: [require('./shared-tailwind-config')],
}
```

**v4:**
```css
@import "./shared-theme.css" layer(theme);
@import "tailwindcss";
```

## Important Modifier

**v3:**
```js
module.exports = { important: true }
```

**v4:**
```css
@import "tailwindcss" important;
```

Or per-rule:
```css
@import "tailwindcss" important ".class-prefix";
```

## Class Strategy for Dark Mode

**v3:**
```js
module.exports = { darkMode: 'class' }
```

**v4:**
```css
@import "tailwindcss";

@variant dark {
  &:where(.dark, .dark *) {
    @slot;
  }
}
```

Then add `dark` class to `<html>` or a parent element.

## Disabling Preflight

**v3:**
```js
module.exports = { corePlugins: { preflight: false } }
```

**v4:**
```css
@import "tailwindcss/utilities";  /* utilities only */
```

Or:
```css
@import "tailwindcss";

/* Override preflight */
@layer base {
  /* your base styles */
}
```

## Source Configuration

**v3:**
```js
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
}
```

**v4:**
```css
@import "tailwindcss";
@source "../pages";
@source "../components";
```

Or with the CLI:
```bash
npx @tailwindcss/cli --content './pages/**/*.{js,ts,jsx,tsx}' --content './components/**/*.{js,ts,jsx,tsx}'
```

