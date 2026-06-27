# 02 — Colors & Themes

## Semantic Color Names

daisyUI adds semantic color names to Tailwind CSS. Use these instead of literal colors (`red-500`, `gray-800`) so they adapt to themes.

| Name | Purpose |
|---|---|
| `primary` | Primary brand color — main brand identity |
| `primary-content` | Foreground content on `primary` background |
| `secondary` | Secondary brand color |
| `secondary-content` | Foreground content on `secondary` background |
| `accent` | Accent brand color for highlights |
| `accent-content` | Foreground content on `accent` background |
| `neutral` | Neutral dark color for non-saturated UI parts |
| `neutral-content` | Foreground content on `neutral` background |
| `base-100` | Base surface color — page background |
| `base-200` | Base color, darker shade for elevations |
| `base-300` | Base color, even darker for deeper elevations |
| `base-content` | Foreground content on `base-*` backgrounds |
| `info` | Informational/helpful messages |
| `info-content` | Foreground on `info` background |
| `success` | Success/safe messages |
| `success-content` | Foreground on `success` background |
| `warning` | Warning/caution messages |
| `warning-content` | Foreground on `warning` background |
| `error` | Error/danger/destructive messages |
| `error-content` | Foreground on `error` background |

## Color Rules

1. Use daisyUI color names in any Tailwind utility: `bg-primary`, `text-base-content`, `border-secondary`
2. daisyUI colors use CSS variables — they change automatically with the active theme
3. No `dark:` prefix needed — colors adapt to the theme
4. Prefer daisyUI colors over Tailwind literal colors so themes work
5. Literal Tailwind colors (`red-500`) stay the same across all themes
6. Avoid Tailwind text colors — `text-gray-800` on dark theme's `bg-base-100` is unreadable
7. `*-content` colors guarantee good contrast with their associated color
8. Use `base-*` for the majority of the page
9. Use `primary` only once, for the most important element

## Built-in Themes

32 built-in themes:

`light`, `dark`, `cupcake`, `bumblebee`, `emerald`, `corporate`, `synthwave`, `retro`, `cyberpunk`, `valentine`, `halloween`, `garden`, `forest`, `aqua`, `lofi`, `pastel`, `fantasy`, `wireframe`, `black`, `luxury`, `dracula`, `cmyk`, `autumn`, `business`, `acid`, `lemonade`, `night`, `coffee`, `winter`, `dim`, `nord`, `sunset`, `caramellatte`, `abyss`, `silk`

Visual preview: https://daisyui.com/theme-generator/

## Custom Theme

```css
@plugin "daisyui";
@plugin "daisyui/theme" {
  name: "mytheme";
  default: true;
  prefersdark: false;
  color-scheme: light;

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

  --radius-selector: 1rem;
  --radius-field: 0.25rem;
  --radius-box: 0.5rem;
  --size-selector: 0.25rem;
  --size-field: 0.25rem;
  --border: 1px;
  --depth: 1;
  --noise: 0;
}
```

All CSS variables above are required. Colors accept OKLCH, hex, or other formats. When generating a custom theme, omit comments.
