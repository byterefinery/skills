# CSS, Fonts, and Distribution

From `docs/browser.md`, `docs/font.md`, `docs/node.md`, and `docs/issues.md` (v0.19.1).

## CSS requirements

KaTeX output is unstyled without the stylesheet. The default build expects fonts in a directory called `fonts` that is a **sibling of `katex.min.css`** — the CSS references them with relative URLs (e.g. `url("fonts/KaTeX_AMS-Regular.woff2")`), so moving or renaming `fonts/` breaks math rendering.

The default CSS uses `font-display: block` to prevent Flash of Unstyled Text (FOUT). To prefer `font-display: swap` (prevents Flash of Invisible Text, FOIT), use `katex-swap.css` / `katex-swap.min.css` instead:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex-swap.min.css" integrity="sha384-/YlNbK67U4WeyjZpwGJd2C4H3Lm8gq0m47PFlrmuKj9TDQzW6HbfSbWI6gpHx2ol" crossorigin="anonymous">
```

To prevent both FOUT and FOIT, prefetch the fonts with the Font Loading API, Web Font Loader, or `rel="preload"`:

```html
<script>
  window.WebFontConfig = {
    custom: {
      families: ['KaTeX_AMS', 'KaTeX_Caligraphic:n4,n7', 'KaTeX_Fraktur:n4,n7',
        'KaTeX_Main:n4,n7,i4,i7', 'KaTeX_Math:i4,i7', 'KaTeX_Script',
        'KaTeX_SansSerif:n4,n7,i4', 'KaTeX_Size1', 'KaTeX_Size2', 'KaTeX_Size3',
        'KaTeX_Size4', 'KaTeX_Typewriter'],
    },
  };
</script>
<script defer src="https://cdn.jsdelivr.net/npm/webfontloader@1.6.28/webfontloader.js" integrity="sha256-4O4pS1SH31ZqrSO2A/2QJTVjTPqVe+jnYgOWUVr7EEc=" crossorigin="anonymous"></script>
```

With `rel="preload"`: add `<link rel="preload" href=(path to WOFF2 font) as="font" type="font/woff2" crossorigin="anonymous">` to `<head>`. Only a few browsers support it, and they all support WOFF2, so preloading WOFF2 fonts is enough.

## Loading patterns

- **Global:** including `katex.js` directly makes `katex` available as a global variable. With `defer`, the object is available after `DOMContentLoaded` fires; without `defer`, immediately after the script tag.
- **Async:** if KaTeX is not critical, add `async` to the script and `rel="preload"` with `onload` to the link (loadCSS pattern).
- **AMD:** `require([".../dist/katex.js"], katex => {...})`.
- **ECMAScript module:** `import katex from 'https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.mjs';` with a `nomodule` fallback script for older browsers.
- **Bundlers:** install via a Node.js package manager and bundle with webpack/rollup — **you have to bundle the stylesheet (`katex.css`) or include it manually.**
- **SRI:** the official docs pin CDN files with `integrity` hashes (see SKILL.md starter template and 02-auto-render.md for the 0.19.1 values for `katex.min.css`, `katex.min.js`, `auto-render.min.js`, and mhchem).

## Self-hosting

Two ways to get a release:

**Option 1 — pre-built release from GitHub.** Each release ships `katex.tar.gz` and `katex.zip` archives under **Assets** — *not* the auto-generated "Source code" download, which only contains the repo source tree without built files. Extracted, you get a `katex/` folder with `katex.js`/`katex.min.js` (UMD), `katex.mjs` (ES module), `katex.css`/`katex.min.css`, `katex-swap.css`/`katex-swap.min.css`, `contrib/` (each extension as `.js`, `.min.js`, `.mjs`), and `fonts/` (WOFF2/WOFF/TTF, required).

**Option 2 — npm.** `npm install katex` (or yarn/pnpm); the hostable files live under `node_modules/katex/dist/` with the same layout. The package also ships unbuilt TypeScript source (`src/`, `contrib/`, `katex.ts`) for bundler users — do not link those from HTML; only `dist/` files are meant to be served as-is.

**Serving:** copy the folder (or the pieces you need plus `fonts/`) into your web server's static directory, e.g.:

```html
<link rel="stylesheet" href="/katex/katex.min.css">
<script defer src="/katex/katex.min.js"></script>
<script defer src="/katex/contrib/auto-render.min.js" onload="renderMathInElement(document.body);"></script>
```

Omit the auto-render script if you only use the JavaScript API. Update is a drop-in replace (same file names and paths every release) — skim the CHANGELOG for breaking changes.

## Font details (`docs/font.md`)

- **Size:** KaTeX math renders in a 1.21× larger font than the surrounding context (easier super/subscripts). Override with CSS, e.g. `.katex { font-size: 1.1em; }`.
- **Units:** all TeX units are supported, including absolute units (`cm`, `in`). Absolute units are scaled relative to the default TeX font size of 10pt (`\kern1cm` ≡ `\kern2.845275em`), so relative and absolute units are uniformly scaled relative to 10pt LaTeX. Because most browsers default to larger fonts, a 1cm kern in KaTeX typically appears larger than 1cm in browser units.
- **Formats:** `ttf` (very old browsers, local install), `woff` (most widely supported), `woff2` (modern browsers, smallest). The build automatically includes only necessary fonts for the Browserslist target.
- **Custom build fonts:** set `USE_(FONT NAME)` environment variables to `"true"`/`"false"` during build to force-include/exclude font types; or use Sass directly:

```scss
@use 'node_modules/katex/src/styles/katex' with (
  $use-ttf: false;
  $use-woff: false;
  $use-woff2: true;
);
```

- **Font location:** the default build expects `fonts/` as a sibling of `katex.min.css`. To relocate: edit `$font-folder` in `src/styles/fonts.scss` (relative or absolute path, e.g. `"/fonts"` or `"../fonts"`), rebuild with `pnpm build`, and use the new `dist/katex.min.css`. Or via Sass: `@use 'node_modules/katex/src/styles/katex' with ($font-folder: "path/to/fonts");`.

## Node.js (`docs/node.md`)

Install: `npm install katex`, `yarn add katex`, `pnpm add katex` (all also support `-g`/`global add`). Deno 2: `deno install katex` / `deno install -g npm:katex`, or import directly from a CDN:

```ts
import katex from "https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.mjs";
```

Importing: CommonJS `const katex = require('katex');` or ESM `import katex from 'katex';` (conditional exports — the ESM build contains ES6 syntax and may need transpiling in old environments).

Including in webpages: to render HTML from `renderToString`, you still need the CSS file, the font files available to the client, and the HTML5 doctype — but you do **not** need `katex.js` on the client.

Building from source: requires Git, Node.js 22.13+, and corepack enabled. `git clone https://github.com/KaTeX/KaTeX.git && cd KaTeX`, then `corepack enable && pnpm install && pnpm build`. The build transpiles and includes only necessary fonts for the Browserslist config (e.g. `BROWSERSLIST="Chrome 68" pnpm build` → no transpilation, WOFF2 only). `USE_(FONT NAME)` env vars override font inclusion. Install the built package by path: `pnpm add /path/to/KaTeX` or `npm install /path/to/KaTeX`. You can also download pre-built packages from GitHub releases.

## Troubleshooting (`docs/issues.md`)

Check the stylesheet loaded and matches the JS version:

```html
<style>
  .katex-version {display: none;}
  .katex-version::after {content:"0.10.2 or earlier";}
</style>
<span class="katex">
  <span class="katex-mathml">The KaTeX stylesheet is not loaded!</span>
  <span class="katex-version katex-rule">KaTeX stylesheet version: </span>
</span>
```

If loaded properly, the version shows (it should match `katex.version` from the JS file); otherwise "The KaTeX stylesheet is not loaded!" is visible.

CSS customization examples:

```css
/* horizontally scrollable display equations */
.katex-display { overflow: auto hidden }

/* allow line breaks in display equations (unlike LaTeX) */
.katex-display > .katex { white-space: normal }
.katex-display > .katex > .katex-html > .katex-base { margin: 0.25em 0 }
.katex-display { margin: 0.5em 0; }
```

Other common issues from `docs/issues.md`:

- `<!DOCTYPE html>` required, even inside `<iframe>`s.
- Smart quotes from Markdown preprocessors (Jekyll, GitHub Pages) break primes (`f'`); workaround: define a single-character macro `{"’": "'"}`.
- KaTeX follows LaTeX's rendering of `aligned`/`matrix` (unlike MathJax): vertical row spacing may be tight — use `\\[0.1em]` to add distance.
- `align` environment is not supported (LaTeX doesn't support `align` in math mode either) — use `aligned`.
- MathJax compatibility: `colorIsTextColor: true` for MathJax-style `\color`; `\class`/`\cssId`/`\style` → `\htmlClass`/`\htmlId`/`\htmlStyle`.
- Some symbols are defined via macros rather than `\DeclareMathSymbol`, so `\expandafter`/`\noexpand` behavior can differ from LaTeX.
