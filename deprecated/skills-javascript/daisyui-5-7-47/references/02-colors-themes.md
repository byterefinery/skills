# daisyUI 5.7.47 Colors and Themes

From the official daisyUI 5.7.47 docs (https://daisyui.com/docs/colors/, https://daisyui.com/themes/).

## Semantic color names

daisyUI adds these semantic names to the Tailwind CSS colors. Each value is a CSS variable of the active theme, so the color changes with `data-theme`.

- `primary` — the main brand color
- `primary-content` — foreground content color for use on `primary`
- `secondary` — an optional secondary brand color
- `secondary-content` — foreground content color for use on `secondary`
- `accent` — an optional accent brand color
- `accent-content` — foreground content color for use on `accent`
- `neutral` — a dark neutral color for UI areas that do not use saturated colors
- `neutral-content` — foreground content color for use on `neutral`
- `base-100` — the page base-surface color for blank backgrounds
- `base-200` — a darker base shade that gives elevation
- `base-300` — a still darker base shade that gives more elevation
- `base-content` — foreground content color for use on a base color
- `info` — information and help messages
- `info-content` — foreground content color for use on `info`
- `success` — success and safe-state messages
- `success-content` — foreground content color for use on `success`
- `warning` — warning and caution messages
- `warning-content` — foreground content color for use on `warning`
- `error` — error, danger, and destructive-action messages
- `error-content` — foreground content color for use on `error`

## Color rules

1. Use daisyUI color names in utility classes as you use other Tailwind CSS color names — `bg-primary`, `border-base-300`, `text-base-content/60`.
2. Do not use the `dark:` variant with daisyUI color names.
3. If possible, use only daisyUI color names — this lets colors change automatically with the theme. A Tailwind CSS color name such as `red-500` stays the same in all themes.
4. Avoid Tailwind CSS color names for text — `text-gray-800` on `bg-base-100` becomes unreadable in a dark theme because `bg-base-100` is dark there.
5. `*-content` colors must have clear contrast with their related colors.
6. Use `base-*` colors for most of the page and the default variant for all elements. Use `primary` only for the most important element on the page, once.
7. In rare cases, use a Tailwind CSS color when content must keep the same color in all themes (e.g., `text-red-500` instead of `text-error`, or a fixed color for an SVG icon or chart).

## Built-in themes

33 built-in themes (from `packages/daisyui/src/themes/` in v5.7.47):

light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk.

The default configuration enables `light` and `dark`. Select themes in the plugin config:

```css
@plugin "daisyui" {
  themes: light --default, dark --prefersdark, cupcake;
}
```

- `themes: all;` enables all built-in themes.
- `themes: false;` disables all built-in themes (usually done before defining only custom themes).

Apply a theme with `data-theme="THEME_NAME"` on `<html>` or any nested element; themes nest with no depth limit. The `--default` flag marks the default theme; `--prefersdark` marks the theme used for `prefers-color-scheme: dark`.

```html
<html data-theme="dark">
  <section data-theme="light">
    <div data-theme="retro">Nested theme</div>
  </section>
</html>
```

The theme-controller component switches themes without `data-theme` — a checked checkbox or radio input with the `theme-controller` class applies its `value` as the theme.

## Custom theme

A CSS file with a custom daisyUI theme has this structure:

```css
@import "tailwindcss";
@plugin "daisyui";
@plugin "daisyui/theme" {
  name: "mytheme";
  default: true; /* set as default */
  prefersdark: false; /* set as default dark mode (prefers-color-scheme:dark) */
  color-scheme: light; /* color of browser-provided UI */

  --color-base-100: oklch(98% 0.02 240);
  --color-base-200: oklch(95% 0.03 240);
  --color-base-300: oklch(92% 0.04 240);
  --color-base-content: oklch(20% 0.05 240);
  --color-primary: oklch(55% 0.3 240);
  --color-primary-content: oklch(98% 0.01 240);
  --color-secondary: oklch(70% 0.25 200);
  --color-secondary-content: oklch(98% 0.01 200);
  --color-accent: oklch(65% 0.25 160);
  --color-accent-content: oklch(98% 0.01 160);
  --color-neutral: oklch(50% 0.05 240);
  --color-neutral-content: oklch(98% 0.01 240);
  --color-info: oklch(70% 0.2 220);
  --color-info-content: oklch(98% 0.01 220);
  --color-success: oklch(65% 0.25 140);
  --color-success-content: oklch(98% 0.01 140);
  --color-warning: oklch(80% 0.25 80);
  --color-warning-content: oklch(20% 0.05 80);
  --color-error: oklch(65% 0.3 30);
  --color-error-content: oklch(98% 0.01 30);

  --radius-selector: 1rem; /* border radius of selectors (checkbox, toggle, badge) */
  --radius-field: 0.25rem; /* border radius of fields (button, input, select, tab) */
  --radius-box: 0.5rem; /* border radius of boxes (card, modal, alert) */
  /* preferred values for --radius-* : 0rem, 0.25rem, 0.5rem, 1rem, 2rem */

  --size-selector: 0.25rem; /* base size of selectors. Keep 0.25rem unless intentionally bigger (0.28125, 0.3125) or smaller (0.21875, 0.1875) */
  --size-field: 0.25rem; /* base size of fields. Keep 0.25rem unless intentionally bigger (0.28125, 0.3125) or smaller (0.21875, 0.1875) */

  --border: 1px; /* border size. Keep 1px unless intentionally 1.5px, 2px, or 0.5px */

  --depth: 1; /* only 0 or 1 — adds a shadow and subtle 3D depth effect to components */
  --noise: 0; /* only 0 or 1 — adds a subtle noise (grain) effect to components */
}
```

Rules for custom themes:

- Include all the CSS variables shown above.
- Colors can use OKLCH, hex, or another format.
- A visual theme generator is available at https://daisyui.com/theme-generator/.

## Change a built-in theme

Use the built-in theme name and change only the necessary values — daisyUI inherits the rest:

```css
@plugin "daisyui/theme" {
  name: "light";
  default: true;
  --color-primary: blue;
  --color-secondary: teal;
}
```

For a custom CDN theme (no build step), define the same variables in a selector that matches the selected `data-theme` and theme controller:

```css
:root:has(input.theme-controller[value=mytheme]:checked),
[data-theme="mytheme"] {
  color-scheme: light;
  --color-primary: oklch(55% 0.3 240);
  /* define the remaining custom-theme variables */
}
```

To make the Tailwind `dark:` variant follow one or more daisyUI themes, define a custom variant:

```css
@custom-variant dark (&:where([data-theme=night], [data-theme=night] *));
```
