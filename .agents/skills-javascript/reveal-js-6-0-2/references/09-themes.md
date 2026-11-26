# Themes

Built-in themes (from `dist/theme/`; importable as `reveal.js/theme/<name>.css`):

beige, black, black-contrast, blood, dracula, league, moon, night, serif, simple, sky, solarized, white, white-contrast

The black theme is the one the demo deck loads by default.

## Using a theme

Script-tag / static HTML:

```html
<link rel="stylesheet" href="dist/theme/black.css" id="theme" />
```

ES modules / bundlers (pattern from the React wrapper docs):

```js
import 'reveal.js/theme/black.css';
```

Swapping themes at runtime is just a `<link>` href change — no re-initialization. The demo deck uses `document.getElementById('theme').setAttribute('href', 'dist/theme/white.css')` in inline handlers.

## Custom themes (SCSS)

Themes are written in Sass under `css/theme/` (source: `css/theme/README.md`). Requires the full reveal.js development environment (npm dependencies, Vite build).

1. Duplicate an existing `.scss` file in `css/theme/`
2. Each theme file includes, in order:
   - `template/mixins.scss` — shared utility functions
   - `template/settings.scss` — the CSS custom variables the template expects; override these to customize
   - `template/theme.scss` — generates the final CSS from the defined variables
   - optionally, custom fonts and additional styles
3. Compile with `npm run build:styles` (Vite, `vite.config.styles.ts`)
