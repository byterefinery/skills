# mhchem Extension

From `contrib/mhchem/README.md` and `docs/node.md` (v0.19.1). Adds the `\ce` and `\pu` functions from the [mhchem](https://mhchem.github.io/MathJax-mhchem/) package for chemical equations and physical units.

## Browser usage

The extension is not part of core KaTeX — the script must be included separately. Write the following into the page's `<head>`. Place it **after** the line that calls `katex.js`, and if using auto-render, **before** the line that calls `auto-render.js`:

```html
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/contrib/mhchem.min.js" integrity="sha384-fB8BH//9nBzROkMUsu/Dr35jWHIbnKesUo9rW0hfEgw8mZGnkAyBAjKX9F98OVuo" crossorigin="anonymous"></script>
```

If you remove the `defer` attribute from the mhchem tag, you must also remove it from the `<script src=".../katex.min.js">` tag.

## Syntax

```js
katex.renderToString("\\ce{H2O -> H2 + O2}");  // chemical equations
katex.renderToString("\\pu{25 mL}");           // physical units
```

The [mhchem Manual](https://mhchem.github.io/MathJax-mhchem/) has the full input syntax with working examples and a demonstration box.

Old versions of `mhchem.sty` used `\cf` for chemical formulas and `\ce` for equations, but `\cf` is deprecated in favor of `\ce`. This extension supports **only `\ce`** — define a macro mapping `\cf` to `\ce` if needed:

```js
katex.renderToString("\\ce{H2O}", { macros: { "\\cf": "\\ce" } });
```

## Node.js usage

The mhchem extension adds its features by **modifying the `katex` module**, so in Node require both (order matters — mhchem after katex):

```js
const katex = require('katex');
require('katex/contrib/mhchem'); // modify katex module
const html = katex.renderToString('\\ce{CO2 + C -> 2 C0}');
```

## Browser support

Tested on Chrome, Firefox, Opera, and Edge.
