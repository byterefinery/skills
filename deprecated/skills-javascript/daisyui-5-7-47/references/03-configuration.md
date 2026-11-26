# daisyUI 5.7.47 Configuration

From the official daisyUI 5.7.47 docs (https://daisyui.com/docs/config/) and the plugin source (`packages/daisyui/index.js`, `functions/pluginOptionsHandler.js`).

## Plugin syntax

daisyUI loads through the Tailwind CSS 4 `@plugin` directive in CSS. All options are optional.

No configuration (defaults):

```css
@plugin "daisyui";
```

All options with their default values:

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

## Options

- **`themes`** — a list of theme names with optional flags, `all`, or `false`. Default: `light --default, dark --prefersdark`. Flags: `--default` (the default theme, applied at `:where(:root)`) and `--prefersdark` (applied under `@media (prefers-color-scheme: dark)` when no `data-theme` attribute is set). `themes: false;` disables all built-in themes — usually set before defining only custom themes.
- **`root`** — the root selector themes apply to. Default: `":root"`. Theme CSS is emitted for `<root>:has(input.theme-controller[value=NAME]:checked), [data-theme=NAME]`.
- **`include`** — only the listed modules (components, base modules, utilities) are compiled.
- **`exclude`** — the listed modules are not compiled. When both `include` and `exclude` are given, a module is included only if it is in `include` and not in `exclude`.
- **`prefix`** — a prefix for all daisyUI classes (e.g., `daisy-` produces `daisy-btn`). Tailwind CSS utilities are not prefixed.
- **`logs`** — set `false` to silence the daisyUI version log line printed on build.

Example — all built-in themes enabled, `bumblebee` default, `synthwave` as the prefers-dark theme, a class prefix, the root scrollbar gutter excluded, logs off:

```css
@plugin "daisyui" {
  themes: light, dark, cupcake, bumblebee --default, emerald, corporate, synthwave --prefersdark, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk;
  root: ":root";
  include: ;
  exclude: rootscrollgutter;
  prefix: daisy-;
  logs: false;
}
```

## Base modules

daisyUI includes the `properties`, `rootcolor`, `scrollbar`, `rootscrolllock`, `rootscrollgutter`, and `svg` base modules. Use `include` or `exclude` with the module name to drop or keep a single module:

```css
@plugin "daisyui" {
  exclude: rootscrollgutter;
}
```

Use `include` or `exclude` for library modules only. For visual changes to existing components, use Tailwind utilities or `@utility` instead.

## Change a component in CSS

Use the Tailwind `@utility` directive to change a daisyUI component globally:

```css
@utility btn {
  @apply rounded-full;
}
```

## Utilities and CSS variables

- Semantic colors work with any Tailwind color utility and opacity modifiers: `bg-primary`, `border-base-300`, `text-base-content/60`.
- `rounded-box`, `rounded-field`, and `rounded-selector` use the radius tokens (`--radius-box`, `--radius-field`, `--radius-selector`) of the active theme.
- `glass` applies the daisyUI glass effect.
- Some components expose CSS variables for component-specific changes: countdown uses `--value` and `--digits`; radial progress uses `--size` and `--thickness`.

## Custom themes

Define a custom theme (or override values of a built-in one) with a separate `@plugin "daisyui/theme"` block:

```css
@plugin "daisyui/theme" {
  name: "mytheme";
  default: true;
  --color-primary: blue;
}
```

A complete custom-theme template with all required CSS variables is in [02-colors-themes](02-colors-themes.md).

## CDN variants

- Main CDN file (light + dark themes only): `https://cdn.jsdelivr.net/npm/daisyui@5`
- All built-in themes: `https://cdn.jsdelivr.net/npm/daisyui@5/themes.css`
- CDN files do not include the `is-drawer-open:` and `is-drawer-close:` variants.

## Framework installs

Each framework or build tool has its own daisyUI install guide — use the file paths and integration steps from the selected guide: https://daisyui.com/docs/install/ (Next.js, Vite, Vite + React, SvelteKit, Vue, Nuxt, Astro, Bun, Preact, Solid, SolidStart, Qwik, HTMX, Rails, Django, Phoenix, Laravel, Elysia, WordPress, Zola, Yew, Dioxus, Lit, Electron, Angular, 11ty, Ember, Fresh, Vike, Rsbuild, UnoCSS, Tailwind CLI, PostCSS, Tailwind standalone).
