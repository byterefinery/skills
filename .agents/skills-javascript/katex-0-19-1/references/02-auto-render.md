# Auto-Render Extension

From `docs/autorender.md` (v0.19.1). The extension automatically renders all math inside text: it searches all text nodes within a given element for the given delimiters, ignoring certain tags, and renders the math in place.

## Loading

The extension is not part of KaTeX proper — include the script in the page along with KaTeX itself.

Classic pattern with `defer` + `onload`:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.css" integrity="sha384-WwGtaC6ywCHxA5cstpj/3+xIZvTez8dq2IcBQaXRkenHZ7FVVq1ZROtURwfbtTlG" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.js" integrity="sha384-a1WQdjRj162i159OYq041X6I4K8NenkrI09LlPmiHg0YOb7CR+wJOraXwK9abpnE" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/contrib/auto-render.min.js" integrity="sha384-bjyGPfbij8/NDKJhSGZNP/khQVgtHUE5exjm4Ydllo42FwIgYsdLO2lXGmRBf5Mz" crossorigin="anonymous"
    onload="renderMathInElement(document.body);"></script>
```

- `defer` means the script doesn't execute until the page has loaded, speeding up page rendering; `onload` calls `renderMathInElement` once the auto-render script loads.
- Alternatively call `renderMathInElement` when (or after) the `DOMContentLoaded` event fires, or in another deferred script — useful for specifying or computing options, or if you don't want `defer`/`onload` attributes:

```html
<script>
    document.addEventListener("DOMContentLoaded", function() {
        renderMathInElement(document.body, {
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false},
                {left: '\\(', right: '\\)', display: false},
                {left: '\\[', right: '\\]', display: true}
            ],
            throwOnError: false
        });
    });
</script>
```

- ES module (also available as `.mjs`):

```html
<script type="module">
    import renderMathInElement from "https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/contrib/auto-render.mjs";
    renderMathInElement(document.body);
</script>
```

Use the `nomodule` attribute to provide a fallback for older browsers without ES module support.

## API

A single function: `window.renderMathInElement(elem, options)`

`elem` is an HTML DOM element; the function recursively searches for text nodes inside it and renders the math in them. `options` accepts the same keys as the object passed to `katex.render`, plus five auto-render-specific keys.

### delimiters

A list of delimiters to look for math, **processed in the same order as the list**. Each entry has three properties:

- `left` — string starting the math expression
- `right` — string ending the math expression
- `display` — whether to render in display mode

Default value:

```js
[
  {left: "$$", right: "$$", display: true},
  {left: "\\(", right: "\\)", display: false},
  {left: "\\begin{equation}", right: "\\end{equation}", display: true},
  {left: "\\begin{align}", right: "\\end{align}", display: true},
  {left: "\\begin{alignat}", right: "\\end{alignat}", display: true},
  {left: "\\begin{gather}", right: "\\end{gather}", display: true},
  {left: "\\begin{CD}", right: "\\end{CD}", display: true},
  {left: "\\[", right: "\\]", display: true}
]
```

To add inline `$...$` support, list it **after** `$$` — because rules are processed in order, putting a `$` rule first would catch `$$` as an empty math expression:

```js
[
  {left: "$$", right: "$$", display: true},
  {left: "$", right: "$", display: false},
  {left: "\\(", right: "\\)", display: false},
  {left: "\\[", right: "\\]", display: true}
]
```

### ignoredTags

DOM node types to ignore when recursing through. Default:

```js
["script", "noscript", "style", "textarea", "pre", "code", "option"]
```

### ignoredClasses

DOM node class names to ignore when recursing through. Not set by default.

### errorCallback

Callback receiving a message and an error stack for critical errors during rendering. Default uses `console.error`.

### preProcess

Callback function `(math: string) => string` used to process math expressions before rendering.

## Notes

- The `displayMode` property of the options object is **ignored** — display mode is taken from the `display` key of the corresponding `delimiters` entry instead.
- The same `options.macros` object (which defaults to an empty object `{}`) is passed into several calls to `katex.render`, so consecutive equations can build up shared macros by `\gdef`.
