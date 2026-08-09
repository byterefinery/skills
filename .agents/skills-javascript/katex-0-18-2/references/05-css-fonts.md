# 05 — CSS & Fonts

## CSS Requirement

KaTeX output requires `katex.min.css` to render correctly. Without it, math elements appear as unstyled HTML spans.

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.18.2/dist/katex.min.css"
      crossorigin="anonymous">
```

The CSS defines:
- Base `.katex` container styles
- Font family assignments (KaTeX_Math, KaTeX_Main, KaTeX_SansSerif, KaTeX_Caligraphic, KaTeX_Script, KaTeX_Fraktur, KaTeX_Bold, KaTeX_Parser, KaTeX_Size1-5)
- Positioning for subscripts, superscripts, fractions, radicals
- AMS environment layout (align, gather, equation)
- Color and sizing classes

## Font Files

KaTeX ships with custom web fonts in `dist/fonts/`. The CSS references them via `@font-face` rules. Font files include `.woff2` and `.ttf` formats.

When self-hosting, ensure:
1. Font files are accessible at the paths referenced by the CSS
2. Server sends correct MIME types: `font/woff2` for `.woff2`, `font/ttf` for `.ttf`
3. CORS headers allow cross-origin font loading if fonts are on a different domain

### Font Families

| Family | Purpose |
|---|---|
| `KaTeX_Main` | Standard math symbols and letters |
| `KaTeX_Math` | Additional math operators and relations |
| `KaTeX_Caligraphic` | Calligraphic letters (`\mathcal`) |
| `KaTeX_Script` | Script letters (`\mathscr`) |
| `KaTeX_Fraktur` | Fraktur/blackletter (`\mathfrak`) |
| `KaTeX_Bold` | Bold variants |
| `KaTeX_SansSerif` | Sans-serif math (`\mathsf`) |
| `KaTeX_Parser` | Typewriter/monospace (`\mathtt`) |
| `KaTeX_Size1`–`KaTeX_Size5` | Scaled sizes for display/subscript modes |

## CDN Setup

jsDelivr CDN (recommended):

```html
<!-- CSS (must come before JS) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.18.2/dist/katex.min.css"
      integrity="sha384-qArEAQvOPs1o7K1iAybhs66g8nYTXVt4VLOQ3abu+OMLJyPNfaH4Wpko0X2epHJ+"
      crossorigin="anonymous">

<!-- Core JS -->
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.2/dist/katex.min.js"
        integrity="sha384-IHT6Yddb0KLCzZaxQ/so1j3xkJ8R6hOkCR06ma9NDHGn0Z4ClKcGtQ6qqsflRPxR"
        crossorigin="anonymous"></script>

<!-- Auto-render extension -->
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.2/dist/contrib/auto-render.min.js"
        integrity="sha384-bjyGPfbij8/NDKJhSGZNP/khQVgtHUE5exjm4Ydllo42FwIgYsdLO2lXGmRBf5Mz"
        crossorigin="anonymous"></script>
```

### Integrity Hashes

Always include `integrity` and `crossorigin="anonymous"` attributes for Subresource Integrity (SRI). Hashes are available in the [KaTeX releases](https://github.com/KaTeX/KaTeX/releases) and on the [jsDelivr package page](https://www.jsdelivr.com/package/npm/katex).

## Self-Hosting

Download from the [releases page](https://github.com/KaTeX/KaTeX/releases) or install via npm:

```bash
npm install katex@0.18.2
```

Copy `node_modules/katex/dist/` to your static assets directory. The directory contains:

```
dist/
├── katex.min.css
├── katex.min.js
├── katex.mjs
├── fonts/
│   ├── KaTeX_*.woff2
│   └── KaTeX_*.ttf
└── contrib/
    ├── auto-render.min.js
    ├── mhchem.min.js
    ├── copy-tex.min.js
    ├── mathtex-script-type.min.js
    └── render-a11y-string.min.js
```

## Server-Side Rendering

When pre-rendering with `renderToString()` on the server:
- Only CSS and fonts are needed on the client
- No JavaScript required if all math is pre-rendered
- Font files can be inlined as base64 data URIs in the CSS for single-file deployment

## Missing Fonts

If font files fail to load:
- Math renders with system font fallbacks
- Layout is typically broken (misaligned symbols, wrong sizes)
- Check browser DevTools Network tab for 404s on font files
- Verify MIME types and CORS headers
