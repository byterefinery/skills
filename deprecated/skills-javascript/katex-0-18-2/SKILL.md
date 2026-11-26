---
name: katex-0-18-2
description: >
  KaTeX renders LaTeX math to fast, print-quality HTML for the web. Use when
  embedding mathematical formulas, equations, or scientific notation in HTML
  pages, docs, or web apps. Covers `katex.render`, `katex.renderToString`,
  auto-render extension, mhchem chemistry, copy-tex, mathtex-script-type,
  render-a11y-string, custom macros, options, and CSS/font setup.
metadata:
  tags:
    - math
    - latex
    - rendering
    - javascript
    - web
---

# katex 0.18.2

## Overview

KaTeX is a fast, self-contained JavaScript library for TeX math rendering in the browser and on Node.js. It produces identical output regardless of environment, supports server-side pre-rendering, and has no runtime dependencies beyond its CSS and font files.

Install via `npm install katex` or load from CDN. The library exports ESM (`.mjs`) and CommonJS (`.js`) builds. Core API provides `katex.render()` (DOM) and `katex.renderToString()` (string). Five contrib extensions add auto-rendering, chemistry formulas, clipboard copy-as-LaTeX, `<script type="math/tex">` support, and accessibility strings.

### Core API

| Function | Purpose |
|---|---|
| `katex.render(tex, element, options?)` | Render TeX into a DOM element |
| `katex.renderToString(tex, options?)` | Return rendered HTML string |
| `katex.version` | Version string (`"0.18.2"`) |
| `katex.ParseError` | Error class for parse failures |

### Options (`KatexOptions`)

| Option | Type | Default | Notes |
|---|---|---|---|
| `displayMode` | `boolean` | `false` | `true` = display (centered, larger) |
| `output` | `"html" \| "mathml" \| "htmlAndMathml"` | `"htmlAndMathml"` | Output format |
| `throwOnError` | `boolean` | `true` | `false` renders errors in `errorColor` |
| `errorColor` | `string` | `"#cc0000"` | Hex color for error rendering |
| `strict` | `boolean \| "ignore" \| "warn" \| "error" \| function` | `"warn"` | LaTeX faithfulness mode |
| `trust` | `boolean \| function` | `false` | Allow `\href`, `\url`, `\includegraphics` |
| `macros` | `Record<string, string \| object \| function>` | — | Custom macro definitions |
| `fleqn` | `boolean` | `false` | Flush-left display math (`\documentclass[fleqn]`) |
| `leqno` | `boolean` | `false` | Left-aligned tags (`\usepackage[leqno]{amsmath}`) |
| `maxSize` | `number` | `Infinity` | Cap on user-specified sizes (ems) |
| `maxExpand` | `number` | `1000` | Max macro expansions |
| `minRuleThickness` | `number` | — | Min thickness in ems for rules/borders |
| `colorIsTextColor` | `boolean` | — | Legacy `\color{blue}{text}` behavior |
| `globalGroup` | `boolean` | `false` | Share macros across render calls |

### Contrib Extensions

| Extension | Import Path | Purpose |
|---|---|---|
| auto-render | `katex/contrib/auto-render` | `renderMathInElement(el, options)` — scan DOM for delimiters |
| mhchem | `katex/contrib/mhchem` | `\ce{}` and `\pu{}` for chemistry formulas and units |
| copy-tex | `katex/contrib/copy-tex` | Copy rendered math as LaTeX source to clipboard |
| mathtex-script-type | `katex/contrib/mathtex-script-type` | Auto-render `<script type="math/tex">` tags |
| render-a11y-string | `katex/contrib/render-a11y-string` | `renderA11yString(tex)` — readable string for screen readers |

## Usage

### CDN Setup

Include the CSS (required), then the JS. Use `defer` on scripts:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.18.2/dist/katex.min.css"
      crossorigin="anonymous">

<script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.2/dist/katex.min.js"
        crossorigin="anonymous"></script>

<script defer src="https://cdn.jsdelivr.net/npm/katex@0.18.2/dist/contrib/auto-render.min.js"
        crossorigin="anonymous"
        onload="renderMathInElement(document.body);"></script>
```

### npm / ESM

```js
import katex from "katex";
import "katex/dist/katex.min.css";

const html = katex.renderToString("E = mc^2", { displayMode: true });
```

### Render to DOM

```js
katex.render("c = \\pm\\sqrt{a^2 + b^2}", element, {
    throwOnError: false
});
```

### Render to String (SSR)

```js
const html = katex.renderToString("\\int_0^\\infty e^{-x} dx = 1", {
    throwOnError: false
});
// '<span class="katex">...</span>'
```

### Auto-Render

Scan a DOM subtree and render all math found between delimiters:

```js
renderMathInElement(document.body, {
    delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false},
        {left: "\\(", right: "\\)", display: false},
        {left: "\\[", right: "\\]", display: true},
    ],
    ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code", "option"],
    ignoredClasses: ["no-render"],
    errorCallback: (msg, err) => console.warn(msg, err.message),
});
```

Default delimiters (without `$…$` to avoid conflicts with currency):

```
$$…$$       — display mode
\(...\)     — inline mode
\begin{equation}…\end{equation}  — display mode
\begin{align}…\end{align}        — display mode
\begin{alignat}…\end{alignat}    — display mode
\begin{gather}…\end{gather}      — display mode
\begin{CD}…\end{CD}              — display mode
\[…\]       — display mode
```

### Custom Macros

Define shorthand commands via the `macros` option:

```js
katex.renderToString("f: \\R^n \\to \\R^m", {
    macros: {
        "\\R": "\\mathbb{R}",
        "\\N": "\\mathbb{N}",
    }
});
```

Function macros receive a `macroExpander` argument:

```js
macros: {
    "\\frown": (macroExpander) => "\\raisebox{0.5ex}{\\text{/}}\\raisebox{-0.5ex}{\\text{\\}}",
}
```

### Trust Handler

Fine-grained control over potentially dangerous commands:

```js
katex.renderToString("\\href{https://example.com}{link}", {
    trust: (context) => {
        if (context.command === "\\href" || context.command === "\\url") {
            return context.protocol === "https:" || context.protocol === "http:";
        }
        return true;
    }
});
```

### mhchem — Chemistry

Load the extension before rendering:

```js
import "katex/contrib/mhchem";

katex.renderToString("\\ce{H2O -> H2 + O2}");
katex.renderToString("\\ce{2H2 + O2 -> 2H2O}");
katex.renderToString("\\pu{25 mL}");
```

### copy-tex — Copy as LaTeX

Automatically intercepts copy events on `.katex` elements and puts the original LaTeX source on the clipboard:

```html
<script src="https://cdn.jsdelivr.net/npm/katex@0.18.2/dist/contrib/copy-tex.min.js"></script>
```

### mathtex-script-type

Replaces `<script type="math/tex">` tags with rendered KaTeX output:

```html
<script type="math/tex">x^2 + y^2 = r^2</script>
<script type="math/tex; mode=display">\sum_{i=1}^n i = \frac{n(n+1)}{2}</script>
```

```html
<script src="https://cdn.jsdelivr.net/npm/katex@0.18.2/dist/contrib/mathtex-script-type.min.js"></script>
```

### render-a11y-string

Generate readable strings for screen readers:

```js
import renderA11yString from "katex/contrib/render-a11y-string";

renderA11yString("\\frac{1}{2}");
// "start fraction, 1, divided by, 2, end fraction"
```

### Error Handling

```js
try {
    katex.render("\\invalid{command}", element);
} catch (e) {
    if (e instanceof katex.ParseError) {
        console.error(`Parse error at position ${e.position}: ${e.rawMessage}`);
    }
}
```

With `throwOnError: false`, invalid LaTeX renders as red text with the error message on hover.

## Gotchas

- **CSS is mandatory** — KaTeX output is unstyled without `katex.min.css`. The CSS references font files (`.woff2`, `.ttf`); ensure font paths resolve correctly when self-hosting.
- **HTML5 doctype required** — Without `<!DOCTYPE html>`, KaTeX may not render properly in quirks mode.
- **`$…$` not enabled by default** — The auto-render extension omits single `$` delimiters because they conflict with currency symbols in prose. Enable explicitly if your content uses them.
- **`throwOnError: true` is the default** — In production, set `throwOnError: false` so invalid input degrades gracefully instead of crashing the page.
- **`trust: false` blocks `\href`, `\url`, `\includegraphics`** — These commands render as errors unless `trust` is `true` or a custom handler returns `true`.
- **`strict: "warn"` is the default** — KaTeX-extensions (not valid LaTeX) produce `console.warn`. Use `strict: true` for LaTeX faithfulness, `strict: "ignore"` for maximum compatibility.
- **`globalGroup: false` isolates macros per call** — Macros defined with `\newcommand` inside one `render()` call do not persist to the next. Set `globalGroup: true` or pass the same `macros` object across calls.
- **`maxSize` caps `\rule` and similar** — Default is `Infinity`. Set a finite value (e.g., `500`) to prevent runaway sizes in untrusted input.
- **`maxExpand` prevents infinite macro loops** — Default 1000. Complex `\edef` expansions count all tokens.
- **Fonts must be served with correct MIME types** — `.woff2` needs `font/woff2`, `.ttf` needs `font/ttf`. Missing fonts fall back to system fonts, which breaks math layout.
- **Server-side rendering needs no JS on the client** — If you pre-render with `renderToString()` on the server, only the CSS and fonts are needed on the client.
- **`output: "mathml"` produces MathML-only** — MathML is supported by modern browsers but lacks the print-quality styling of KaTeX's HTML output. Use `"htmlAndMathml"` for best accessibility.
- **mhchem is a separate import** — `\ce{}` and `\pu{}` do not work without loading `katex/contrib/mhchem`.
- **copy-tex replaces clipboard content globally** — It intercepts all copy events within `.katex` elements. Do not combine with other clipboard handlers on the same elements.
- **`renderA11yString` output is approximate** — Complex expressions produce literal token descriptions (e.g., "f, left parenthesis, x") rather than semantic readings.

## References

- [01-api-options](references/01-api-options.md) — Full `KatexOptions` reference, `TrustContext`, `StrictFunction` types
- [02-auto-render](references/02-auto-render.md) — `renderMathInElement` options, delimiter specs, ignored tags/classes
- [03-mhchem](references/03-mhchem.md) — Chemistry formulas with `\ce{}` and `\pu{}`, syntax rules
- [04-error-handling](references/04-error-handling.md) — `ParseError` properties, `throwOnError` modes, custom error rendering
- [05-css-fonts](references/05-css-fonts.md) — CSS requirements, font file paths, self-hosting, CDN integrity hashes
- [06-macros](references/06-macros.md) — Macro definitions, function macros, `globalGroup`, `\def`/`\newcommand`/`\gdef`
- [07-extensions](references/07-extensions.md) — copy-tex, mathtex-script-type, render-a11y-string details
