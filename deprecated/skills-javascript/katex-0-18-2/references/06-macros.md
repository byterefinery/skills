# 06 — Macros

## Defining Macros

Custom macros extend KaTeX's LaTeX vocabulary. Define them via the `macros` option:

```js
katex.renderToString("\\f{\\R^n}", {
    macros: {
        "\\R": "\\mathbb{R}",
        "\\N": "\\mathbb{N}",
        "\\Z": "\\mathbb{Z}",
    }
});
```

## Macro Syntax

### Simple Expansion

String values are substituted verbatim:

```js
macros: {
    "\\real": "\\mathbb{R}",
    "\\im": "\\Im",
    "\\Re": "\\Re",
    "\\abs": "\\left| #1 \\right|",  // with argument
}
```

### Argumented Macros

Use `#1`, `#2`, etc. for positional arguments:

```js
macros: {
    "\\abs": "\\left| #1 \\right|",
    "\\pair": "(#1, #2)",
    "\\vec": "\\overrightarrow{#1}",
}
```

```js
katex.renderToString("\\abs{x^2}", {
    macros: { "\\abs": "\\left| #1 \\right|" }
});
```

### Function Macros

Function values receive a `macroExpander` for dynamic expansion:

```js
macros: {
    "\\frown": (macroExpander) =>
        "\\raisebox{0.5ex}{\\text{/}}\\raisebox{-0.5ex}{\\text{\\}}",
    "\\myfrac": (macroExpander) => {
        const num = macroExpander.expandArgs(1)[0];
        return `\\frac{${num}}{2}`;
    }
}
```

## Built-in Definition Commands

KaTeX supports these LaTeX macro definition commands:

| Command | Scope | Description |
|---|---|---|
| `\def\cmd{expansion}` | Local | Define/override a command |
| `\gdef\cmd{expansion}` | Global | Define globally (persists if `globalGroup: true`) |
| `\newcommand{\cmd}{expansion}` | Local | Define only if not already defined |
| `\renewcommand{\cmd}{expansion}` | Local | Redefine an existing command |
| `\providecommand{\cmd}{expansion}` | Local | Define only if not already defined |

With optional arity:

```latex
\newcommand{\abs}[1]{\left|#1\right|}
\newcommand{\pair}[2]{(#1,#2)}
```

## globalGroup

By default (`globalGroup: false`), each render call runs in an isolated group. Macros defined inside one call do not affect the next:

```js
// These are isolated — \foo is not available in the second call
katex.renderToString("\\newcommand{\\foo}{x} \\foo", element1);
katex.renderToString("\\foo", element2);  // Error: \foo undefined
```

With `globalGroup: true`, top-level definitions persist:

```js
const macros = {};

katex.renderToString("\\newcommand{\\foo}{x}", element1, {
    globalGroup: true,
    macros: macros,
});

katex.renderToString("\\foo", element2, {
    globalGroup: true,
    macros: macros,  // \foo is now available
});
```

## Macro Sharing Pattern

For multiple render calls that share macros:

```js
const sharedMacros = {
    "\\R": "\\mathbb{R}",
    "\\N": "\\mathbb{N}",
};

function render(tex, element) {
    katex.render(tex, element, {
        macros: sharedMacros,
        globalGroup: true,
    });
}
```

## Limitations

- Macros cannot reference DOM elements or JavaScript values directly
- Function macros run during parsing, not rendering — they return LaTeX strings, not HTML
- Recursive macros are limited by `maxExpand` (default 1000)
- `\edef` fully expands all tokens and counts against `maxExpand`
