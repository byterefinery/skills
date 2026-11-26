---
name: katex-0-19-1
description: KaTeX 0.19.1 renders LaTeX math to fast, print-quality HTML for the web and Node.js. Use when embedding mathematical formulas, equations, or scientific notation in HTML pages, docs, or web apps. Covers katex.render, renderToString, auto-render extension, mhchem chemistry, copy-tex, mathtex-script-type, render-a11y-string, custom macros, trust and strict options, CSS/font self-hosting, and v0.19 strict metrics changes.
license: MIT
metadata:
  tags:
    - math
    - latex
    - rendering
    - javascript
    - web
---

# katex 0.19.1

## Overview

KaTeX is a fast JavaScript library for synchronous TeX math typesetting in browsers and Node.js. It is print-quality (layout based on Donald Knuth's TeX), self-contained with no runtime dependencies beyond its CSS and fonts, and produces identical output regardless of environment — so you can pre-render with `renderToString()` on a server and ship plain HTML. It exports ESM (`.mjs`) and CommonJS (`.js`) builds for every entry point.

Test any expression against the full option set (`displayMode`, `leqno`, `fleqn`, `throwOnError`, `strict`, `output`, `trust`, `macros`) on the live demo page at `https://katex.org/#demo`.

v0.19.0 (first shipped in 0.18.11) changed `strict` behavior: missing character metrics are now reported through `strict` with error code `symbolNotInFont`, and `strict` functions must return a value. v0.19.1 fixes percent signs in raw argument types. See `## Gotchas`.

### Core API

| Function | Purpose |
|---|---|
| `katex.render(tex, element, options?)` | Render TeX into a DOM element |
| `katex.renderToString(tex, options?)` | Return rendered HTML string |
| `katex.version` | Version string (`"0.19.1"`) |
| `katex.ParseError` | Error class; properties `position`, `length`, `rawMessage`, `message` |

### Options (`KatexOptions`)

| Option | Type | Default | Notes |
|---|---|---|---|
| `displayMode` | `boolean` | `false` | `true` = display (centered, `\displaystyle`, no auto line breaks) |
| `output` | `"html" \| "mathml" \| "htmlAndMathml"` | `"htmlAndMathml"` | Markup language of the output |
| `leqno` | `boolean` | `false` | Display `\tag`s on the left (`\usepackage[leqno]{amsmath}`) |
| `fleqn` | `boolean` | `false` | Flush-left display math, 2em left margin (`\documentclass[fleqn]`) |
| `throwOnError` | `boolean` | `true` | `false` renders invalid input in `errorColor` with hover text |
| `errorColor` | `string` | `"#cc0000"` | `"#XXX"` or `"#XXXXXX"` color for errors and unsupported commands |
| `macros` | `object` | — | Custom macros; keys `\foo` or single chars; values string / function / expansion object |
| `minRuleThickness` | `number` | — | Min thickness in ems for rules (usual value 0.04; use >0.04 to have effect) |
| `colorIsTextColor` | `boolean` | `false` | Old `\color{blue}{text}` behavior (KaTeX <0.8.0 / MathJax-style) |
| `maxSize` | `number` | `Infinity` | Cap on user-specified sizes (ems), e.g. `\rule{500em}{500em}` |
| `maxExpand` | `number` | `1000` | Max macro expansions; `\edef` counts all expanded tokens |
| `strict` | `boolean \| "ignore" \| "warn" \| "error" \| function` | `"warn"` | LaTeX faithfulness mode; function receives `(errorCode, errorMsg, token?)` |
| `trust` | `boolean \| function` | `false` | Allow `\url`, `\href`, `\includegraphics`, `\htmlClass`, `\htmlId`, `\htmlStyle`, `\htmlData` |
| `globalGroup` | `boolean` | `false` | `\def`/`\newcommand` at top level land in `macros` for later calls |

Full details, `strict` error codes, and `trust` context shapes in [01-api-options](references/01-api-options.md).

### Contrib Extensions

| Extension | Import Path | Purpose |
|---|---|---|
| auto-render | `katex/contrib/auto-render` | `renderMathInElement(el, options)` — scan DOM for delimiters |
| mhchem | `katex/contrib/mhchem` | `\ce{}` and `\pu{}` for chemistry formulas and units |
| copy-tex | `katex/contrib/copy-tex` | Copy rendered math as LaTeX source to clipboard (no CSS since v0.16) |
| mathtex-script-type | `katex/contrib/mathtex-script-type` | Render `<script type="math/tex">` tags |
| render-a11y-string | `katex/contrib/render-a11y-string` | `renderA11yString(tex)` — readable string for screen readers |

## Usage

### CDN Setup (Starter Template)

The official starter template, pinned to 0.19.1 with SRI integrity hashes:

```html
<!DOCTYPE html>
<html>
  <head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.css" integrity="sha384-WwGtaC6ywCHxA5cstpj/3+xIZvTez8dq2IcBQaXRkenHZ7FVVq1ZROtURwfbtTlG" crossorigin="anonymous">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.js" integrity="sha384-a1WQdjRj162i159OYq041X6I4K8NenkrI09LlPmiHg0YOb7CR+wJOraXwK9abpnE" crossorigin="anonymous"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/contrib/auto-render.min.js" integrity="sha384-bjyGPfbij8/NDKJhSGZNP/khQVgtHUE5exjm4Ydllo42FwIgYsdLO2lXGmRBf5Mz" crossorigin="anonymous"
        onload="renderMathInElement(document.body);"></script>
  </head>
</html>
```

`defer` speeds page rendering; the `onload` attribute triggers auto-render once the extension loads. Alternatively call `renderMathInElement` from a `DOMContentLoaded` listener (useful for computing options). ES module form: `import renderMathInElement from "https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/contrib/auto-render.mjs"` (add a `nomodule` fallback for old browsers).

### npm / ESM

```js
import katex from "katex";
import "katex/dist/katex.min.css";

const html = katex.renderToString("E = mc^2", { displayMode: true });
```

CommonJS: `const katex = require("katex");` — note the ESM build uses ES6 syntax and may need transpiling in old environments. Deno 2: `deno install -g npm:katex`, or import directly from a CDN (`https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.mjs`).

### Render to DOM

```js
katex.render("c = \\pm\\sqrt{a^2 + b^2}", element, {
    throwOnError: false
});
```

Use `String.raw` to avoid double backslashes (but you cannot escape `${` or backticks inside it):

```js
katex.render(String.raw`c = \pm\sqrt{a^2 + b^2}`, element, { throwOnError: false });
```

### Render to String (SSR)

```js
var html = katex.renderToString("c = \\pm\\sqrt{a^2 + b^2}", {
    throwOnError: false
});
// '<span class="katex">...</span>'
```

The client still needs the CSS and font files — but not `katex.js`.

### Auto-Render

Scan a DOM subtree and render all math found between delimiters. Options accept every `KatexOptions` key plus five auto-render keys (`delimiters`, `ignoredTags`, `ignoredClasses`, `errorCallback`, `preProcess`); `displayMode` is ignored and taken from each delimiter's `display` key instead:

```js
renderMathInElement(document.body, {
    delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false},
        {left: "\\(", right: "\\)", display: false},
        {left: "\\[", right: "\\]", display: true}
    ],
    throwOnError: false
});
```

`$…$` inline math is **not** a default delimiter (currency conflict) — and if you add it, list it *after* `$$…$$`, because rules are processed in order. The same `options.macros` object (default `{}`) is passed into every `katex.render` call, so `\gdef` macros accumulate across equations.

### mhchem — Chemistry

Include the contrib script *after* `katex.js` and *before* `auto-render.js` (if using both). If you remove `defer` from the mhchem tag, remove it from the `katex.min.js` tag too:

```html
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/contrib/mhchem.min.js" integrity="sha384-fB8BH//9nBzROkMUsu/Dr35jWHIbnKesUo9rW0hfEgw8mZGnkAyBAjKX9F98OVuo" crossorigin="anonymous"></script>
```

```js
katex.renderToString("\\ce{H2O -> H2 + O2}");   // chemical equations
katex.renderToString("\\pu{25 mL}");            // physical units
```

Only `\ce{}` is supported for formulas (`\cf` is deprecated — define a macro `\cf → \ce` if needed). Full syntax: the [mhchem Manual](https://mhchem.github.io/MathJax-mhchem/).

### Strict and Trust (v0.19 behavior)

`strict` controls LaTeX faithfulness. Since v0.19.0, symbols with no character metrics (e.g. `\origof`, `\char"20AC`) are reported via `strict` with error code `symbolNotInFont`: the default `strict: "warn"` still warns (new message format), `strict: "error"`/`true` now **throws**, `strict: "ignore"`/`false` silences it. A `strict` function **must return a value** — `undefined`/`null` now behave like `"warn"`, not `"ignore"`:

```js
katex.render(tex, element, {
    strict: (errorCode) =>
        errorCode === "symbolNotInFont" ? "warn" : "error",
});
```

`trust` gates commands that can load external resources or set HTML attributes. Default `false` renders them in `errorColor`. A custom handler receives a context object:

```js
katex.renderToString("\\href{https://example.com}{link}", {
    trust: (context) => context.protocol === "https" || context.protocol === "http",
});
```

Context shapes: `{command: "\\url"|"\\href"|"\\includegraphics", url, protocol?}` (protocol lowercased, `"_relative"` for relative URLs), `{command: "\\htmlClass", class}`, `{command: "\\htmlId", id}`, `{command: "\\htmlStyle", style}`, `{command: "\\htmlData", attributes}`.

### Error Handling

```js
try {
    var html = katex.renderToString(texString);
} catch (e) {
    if (e instanceof katex.ParseError) {
        // escape & < > before putting source or message into HTML
        html = ("Error in LaTeX '" + texString + "': " + e.message)
            .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    } else {
        throw e;
    }
}
```

Failure to escape makes a `<script>` injection possible with untrusted input. Alternatively `throwOnError: false` renders the source in `errorColor` with the error as hover text.

### Self-Hosting

Download the release archive (`katex.tar.gz` / `katex.zip` under **Assets** — not the auto-generated "Source code" download, which has no built files) or copy `node_modules/katex/dist/` from npm. The `fonts/` directory **must stay alongside the CSS** — `katex.css` references fonts via relative URLs (`url("fonts/KaTeX_AMS-Regular.woff2")`). Updates are a drop-in replace; skim the CHANGELOG between versions.

## Gotchas

- **CSS is mandatory** — KaTeX output is unstyled without `katex.min.css`, and the CSS needs the `fonts/` directory as a sibling. Moving or renaming `fonts/` breaks math rendering.
- **HTML5 doctype required** — without `<!DOCTYPE html>` the browser renders in quirks mode and KaTeX may misrender. This applies even inside `<iframe>`s (they don't inherit the parent's doctype).
- **`$…$` not enabled by default** — auto-render omits single-`$` delimiters (currency conflict). When enabling, list `{left: "$", right: "$"}` *after* `$$` in `delimiters`, or `$` rules catch `$$` as an empty expression.
- **`throwOnError: true` is the default** — invalid LaTeX throws `ParseError` and can crash a render loop. Set `throwOnError: false` for user-supplied input.
- **`trust: false` is the default** — `\href`, `\url`, `\includegraphics`, `\htmlClass`, `\htmlId`, `\htmlStyle`, `\htmlData` render in `errorColor` unless `trust` is `true` or your handler returns true.
- **v0.19 breaking — `strict` changes** — missing character metrics now go through `strict` as `symbolNotInFont` (old `No character metrics for '…'` console.warn message is gone; update code matching on it), `strict: "error"` now throws for such input, and `strict` functions returning `undefined`/`null` are treated as `"warn"` (return `false` or `"ignore"` explicitly to suppress). TypeScript: `StrictFunction` no longer returns `undefined` and its `token` parameter is optional (`token?`).
- **v0.18 breaking — CSS class prefixes** — internal classes are prefixed `katex-` (`.base` → `.katex-base`, `.root` → `.katex-root`, …). Update custom styles and sanitizer allowlists targeting KaTeX internals.
- **`macros` must be shared for `\gdef` persistence** — `\gdef` writes into the `macros` object you pass. Create one object outside a loop and reuse it; a fresh `{}` per call loses definitions. Persistent macros can redefine standard commands, so only share a `macros` object across content of common trust (e.g. one user's messages), never across untrusted users.
- **Escape error output** — `ParseError.message` and the TeX source contain raw `&`, `<`, `>`; escape them before inserting into HTML to prevent script injection.
- **`globalGroup: false` isolates `\def`/`\newcommand` per call** — top-level definitions do not persist unless you set `globalGroup: true` (or use `\gdef` with a shared `macros` object).
- **`maxSize` is `Infinity` by default** — untrusted input can emit `\rule{500em}{500em}`; cap it (also `maxExpand` defaults to 1000 against infinite macro loops).
- **`align` environment is not supported** — LaTeX itself doesn't support `align` in math mode; use `aligned`, which offers the same functionality.
- **MathJax porting** — set `colorIsTextColor: true` for MathJax-style `\color{blue}{text}`; `\class`/`\cssId`/`\style` become `\htmlClass`/`\htmlId`/`\htmlStyle`.
- **Smart quotes break primes** — Markdown preprocessors (Jekyll, GitHub Pages) turn `'` into `’`, breaking `f'`. Define a single-character macro `{"’": "'"}` in `macros`.
- **`font-display: block` by default** — use `katex-swap.min.css` instead of `katex.min.css` if you prefer `font-display: swap` (avoids FOIT at the cost of FOUT).
- **Bundlers do not auto-include the CSS** — when bundling with webpack/rollup, `katex.css` must be bundled or linked manually.
- **`minRuleThickness` needs a value above 0.04** — the usual rule thickness is 0.04em, so a value like `0.05`/`0.06` is needed for the minimum to have any effect; negative values are ignored.
- **copy-tex has no CSS since v0.16** — remove any `copy-tex.css` import or `<link>`.
- **Macro symbols may behave unlike LaTeX** — some symbols are defined as macros (expanding to multiple tokens), so `\expandafter`/`\noexpand` around them can differ from LaTeX.

## References

- [01-api-options](references/01-api-options.md) — Full `KatexOptions` details, all `strict` error codes, `trust` context shapes and sample handlers, persistent macros
- [02-auto-render](references/02-auto-render.md) — `renderMathInElement` API, all five extension keys, default delimiters, loading patterns
- [03-mhchem](references/03-mhchem.md) — `\ce{}` / `\pu{}` usage, script loading order, Node.js usage
- [04-error-handling](references/04-error-handling.md) — `ParseError` anatomy, escaping rules, security options, vulnerability reporting
- [05-css-fonts](references/05-css-fonts.md) — CDN with SRI, self-hosting, fonts layout, font formats, swap variant, webfont loading, Node/bundler/build-from-source, troubleshooting
- [06-macros](references/06-macros.md) — Macro value types, `\gdef` persistence, `globalGroup`, `\let` simulation, security
- [07-extensions](references/07-extensions.md) — copy-tex, mathtex-script-type, render-a11y-string, third-party libraries
