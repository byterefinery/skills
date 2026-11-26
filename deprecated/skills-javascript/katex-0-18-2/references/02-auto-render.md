# 02 — Auto-Render

## renderMathInElement

The auto-render extension scans a DOM element and its descendants, finding TeX math between delimiter pairs and rendering each match with KaTeX.

```js
import renderMathInElement from "katex/contrib/auto-render";

renderMathInElement(document.body, {
    delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "\\(", right: "\\)", display: false},
        {left: "\\[", right: "\\]", display: true},
    ],
    ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code", "option"],
    ignoredClasses: ["no-render"],
    errorCallback: (msg, err) => console.warn(msg, err.message),
});
```

## Options

### delimiters

- **Type:** `DelimiterSpec[]`
- **Default:** `$$…$$`, `\(...\)`, `\begin{equation}…\end{equation}`, `\begin{align}…\end{align}`, `\begin{alignat}…\end{alignat}`, `\begin{gather}…\end{gather}`, `\begin{CD}…\end{CD}`, `\[…\]`

Array of delimiter specifications. Each entry has `left`, `right`, and `display`:

```ts
interface DelimiterSpec {
    left: string;
    right: string;
    display: boolean;
}
```

Order matters — `$$` must be listed before `$` so the parser matches the longer delimiter first.

Default delimiters (single `$…$` is commented out to avoid currency symbol conflicts):

```js
[
    {left: "$$", right: "$$", display: true},
    {left: "\\(", right: "\\)", display: false},
    {left: "\\begin{equation}", right: "\\end{equation}", display: true},
    {left: "\\begin{align}", right: "\\end{align}", display: true},
    {left: "\\begin{alignat}", right: "\\end{alignat}", display: true},
    {left: "\\begin{gather}", right: "\\end{gather}", display: true},
    {left: "\\begin{CD}", right: "\\end{CD}", display: true},
    {left: "\\[", right: "\\]", display: true},
]
```

### preProcess

- **Type:** `(math: string) => string`

Transform the math string before rendering. Useful for adding custom preprocessing or normalizing input.

```js
preProcess: (math) => math.replace(/\\,/g, "\\, ")
```

### ignoredTags

- **Type:** `string[]`
- **Default:** `["script", "noscript", "style", "textarea", "pre", "code", "option"]`

HTML tag names to skip entirely. Text nodes inside these elements are not scanned for delimiters.

### ignoredClasses

- **Type:** `string[]`
- **Default:** `[]`

CSS class names. Any element with one of these classes (or its descendants) is skipped.

```js
ignoredClasses: ["no-render", "raw-latex"]
```

### errorCallback

- **Type:** `(msg: string, err: Error) => void`
- **Default:** `console.error`

Called when a math expression fails to parse. The text node is left as raw text (the original delimiters and content are preserved).

```js
errorCallback: (msg, err) => {
    console.warn(msg, err.message);
    // Optionally track analytics, log to server, etc.
}
```

### macros

- **Type:** `Record<string, string>`

Custom macros available to all expressions rendered in this call. Shared across all matches within a single `renderMathInElement` call.

## Delimiter Matching Rules

- Brace-aware: `{` and `}` inside math increase/decrease brace level; delimiters inside braces are not matched.
- Escape-aware: `\` skips the next character during delimiter search.
- AMS environments: `\begin{equation}`, `\begin{align}`, etc. are matched even without surrounding `$$…$$`.
- Order matters: list `$$` before `$` so the regex matches `$$` first.

## Performance Notes

- Auto-render walks the entire DOM subtree. For large documents, consider rendering only specific containers.
- Text nodes are concatenated with siblings before scanning (WebKit splits large text nodes).
- For static content, prefer server-side rendering with `renderToString()` over client-side auto-render.
