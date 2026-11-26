# Macros

From `docs/options.md` (macros, globalGroup), `docs/api.md` (Persistent Macros, Security of Persistent Macros), and the demo page (`static/`) (v0.19.1).

## Macro value types

The `macros` option takes an object whose keys are either a backslash-prefixed command name (`"\\foo"` defines `\foo`) or a single character (the equivalent of a TeX active character). Each value is one of:

**String** — the LaTeX expansion, recursively expanded when used. Can invoke required arguments via `#1`, `#2`, etc.:

```js
katex.renderToString("f: \\R^n \\to \\R^m", {
    macros: {
        "\\R": "\\mathbb{R}",
        "\\N": "\\mathbb{N}",
    }
});

// argument macros — the demo page's own default example:
macros: { "\\f": "#1f(#2)" }
```

**Function** — accepts an instance of `MacroExpander` as first argument and returns the expansion string. `MacroExpander` is an internal API, subject to non-backwards compatible changes (see `src/defineMacro.js`):

```js
macros: {
    "\\frown": (macroExpander) => "\\raisebox{0.5ex}{\\text{/}}\\raisebox{-0.5ex}{\\text{\\}}",
}
```

**Expansion object** — matches the internal `MacroExpansion` specification, which is what results from global `\def` or `\let`. Simulate `\let\realint=\int` via:

```js
{"\\realint": {tokens: [{text: "\\int", noexpand: true}], numArgs: 0}}
```

## The `macros` object is modified in place

If the LaTeX code defines its own macros via `\gdef` or `\global\let` (or via `\def`/`\newcommand`/`\let` when using `globalGroup`), KaTeX writes those definitions into the `macros` object. Passing the same object into consecutive calls shares state across calls — in particular user macro definitions.

### Persistent macros (`\gdef`)

To make `\gdef` macros persist between KaTeX elements, create **one shared `macros` object** outside the loop and pass it into every call. Do not create a fresh `macros` object for each call:

```js
const macros = {};
for (let element of mathElements) {
    katex.render(element.textContent, element, {
        throwOnError: false,
        macros
    });
}
```

If an author uses `\gdef`, KaTeX inserts the definition into `macros`, which continues to exist between calls.

Auto-render does this automatically: its `options.macros` (default `{}`) is the same object passed into every `katex.render` call, so consecutive equations build up shared macros by `\gdef`.

### Security of persistent macros

Persistent macros can change KaTeX's behavior (e.g. redefining standard commands). For security, use a shared `macros` object only for multiple elements of **common trust** — e.g. create one `macros` object per user's message, but not across messages posted by multiple users.

## `globalGroup`

`globalGroup: true` runs KaTeX code in the global group: top-level `\def` and `\newcommand` definitions are added to the `macros` argument and can be used in subsequent render calls. Without it, top-level `\def`/`\newcommand` are local (like LaTeX, where `\begin{equation}` and `$$` create a local group).

```js
const macros = { "\\RR": "\\mathbb{R}" };
katex.renderToString("\\let\\root=\\sqrt", {
    globalGroup: true,  // or use \global\let
    macros,
});
// macros now has a definition for "\\root"
katex.render("c = \\pm\\root{a^2 + b^2}\\in\\RR", element, {
    displayMode: true,
    macros,
});
```

## Related

- Single-character macros fix smart-quote breakage: `{"’": "'"}` (Jekyll/GitHub Pages convert `'` to `’`, breaking `f'`).
- Some KaTeX symbols are themselves defined via macros (expanding to multiple tokens), so `\expandafter`/`\noexpand` around them may behave differently than in LaTeX (`docs/issues.md`).
- `maxExpand` (default `1000`) caps macro expansions; `Infinity` fully expands, as in LaTeX.
