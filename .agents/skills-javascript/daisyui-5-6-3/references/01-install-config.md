# 01 — Install & Config

## Installation

### npm (recommended)

Install as a dev dependency:
```bash
npm i -D daisyui@latest
```

Add to your CSS file:
```css
@import "tailwindcss";
@plugin "daisyui";
```

### CDN (prototyping only)

```html
<link href="https://cdn.jsdelivr.net/npm/daisyui@5" rel="stylesheet" type="text/css" />
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
```

## Config

### No config (defaults)

```css
@plugin "daisyui";
```

Enables `light` as default theme and `dark` as prefers-color-scheme dark mode.

### Themes only

```css
@plugin "daisyui" {
  themes: light --default;
}
```

### All default config options

```css
@plugin "daisyui" {
  themes: light --default, dark --prefersdark;
  root: ":root";
  include: ;
  exclude: ;
  prefix: ;
  logs: true;
}
```

### Example: full config

```css
@plugin "daisyui" {
  themes: light, dark, cupcake, bumblebee --default, emerald, corporate, synthwave --prefersdark, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk;
  root: ":root";
  include: ;
  exclude: rootscrollgutter, checkbox;
  prefix: daisy-;
  logs: false;
}
```

## Config Options

| Option | Description |
|---|---|
| `themes` | Comma-separated theme names. Append `--default` for default theme or `--prefersdark` for dark mode theme |
| `root` | CSS selector where theme variables are applied (default: `:root`) |
| `include` | Comma-separated list of components to include (empty = all) |
| `exclude` | Comma-separated list of components to exclude (e.g., `checkbox`, `rootscrollgutter`) |
| `prefix` | Prefix added to all daisyUI class names (e.g., `daisy-` makes `btn` → `daisy-btn`) |
| `logs` | Enable/disable console logs (default: `true`) |

## Theme Switching

Switch themes at runtime by setting `data-theme` on `<html>`:
```html
<html data-theme="cupcake">
```

Use the [theme-controller](references/10-interactive.md) component for checkbox/radio-based theme switching.
