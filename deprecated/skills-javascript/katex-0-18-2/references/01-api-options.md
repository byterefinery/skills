# 01 — API & Options

## KatexOptions

Full reference for all options accepted by `katex.render()` and `katex.renderToString()`.

### displayMode

- **Type:** `boolean`
- **Default:** `false`

When `true`, math is rendered in display mode — centered on its own line with larger sizing, matching `$$…$$` or `\[…\]` behavior. When `false`, math renders inline with surrounding text, matching `$…$` or `\[…\]`.

```js
katex.renderToString("E = mc^2", { displayMode: true });
```

### output

- **Type:** `"html" | "mathml" | "htmlAndMathml"`
- **Default:** `"htmlAndMathml"`

Controls the output markup:

| Value | Output |
|---|---|
| `"html"` | HTML spans only — fastest rendering, visual only |
| `"mathml"` | `<math>` element only — accessible but less print-quality |
| `"htmlAndMathml"` | Both — HTML for display, MathML nested for screen readers |

### throwOnError

- **Type:** `boolean`
- **Default:** `true`

When `true`, invalid LaTeX throws a `ParseError`. When `false`, invalid commands render as text in `errorColor` with the error message available on hover.

For production apps with user-supplied input, always set `throwOnError: false`.

### errorColor

- **Type:** `string` (hex color `"#XXX"` or `"#XXXXXX"`)
- **Default:** `"#cc0000"`

Color used when `throwOnError: false` to render unsupported commands and invalid LaTeX.

### strict

- **Type:** `boolean | "ignore" | "warn" | "error" | StrictFunction`
- **Default:** `"warn"`

Controls LaTeX faithfulness:

| Value | Behavior |
|---|---|
| `false` / `"ignore"` | Allow KaTeX extensions (MathJax-compatible) |
| `true` / `"error"` | Throw on any non-LaTeX feature |
| `"warn"` | `console.warn` on non-LaTeX features |
| `function` | Custom handler per error code |

Error codes a custom handler receives:

| Code | Meaning |
|---|---|
| `"unknownSymbol"` | Unknown symbol in math mode |
| `"unicodeTextInMathMode"` | Unicode text outside `\text{}` |
| `"mathVsTextUnits"` | Math units used in text or vice versa |
| `"commentAtEnd"` | `%` comment at end of input |
| `"htmlExtension"` | HTML extension like `\htmlClass` |
| `"newLineInDisplayMode"` | Newline in display mode |

```js
katex.renderToString("x", {
    strict: (errorCode, errorMsg, token) => {
        if (errorCode === "htmlExtension") return "error";
        return "ignore";
    }
});
```

### trust

- **Type:** `boolean | (context: TrustContext) => boolean`
- **Default:** `false`

Controls potentially dangerous commands:

| Command | Context Properties |
|---|---|
| `\url` | `url`, `protocol?` |
| `\href` | `url`, `protocol?` |
| `\includegraphics` | `url`, `protocol?` |
| `\htmlClass` | `class` |
| `\htmlId` | `id` |
| `\htmlStyle` | `style` |
| `\htmlData` | `attributes: Record<string, string>` |

```js
katex.renderToString("\\url{https://example.com}", {
    trust: (ctx) => {
        if (ctx.command === "\\url") {
            return ctx.protocol === "https:";
        }
        return false;
    }
});
```

### macros

- **Type:** `Record<string, string | object | ((macroExpander) => string | object)>`

Custom macro definitions. Keys are the command name (including backslash), values are expansion strings or functions.

```js
macros: {
    "\\R": "\\mathbb{R}",
    "\\N": "\\mathbb{N}",
    "\\Z": "\\mathbb{Z}",
    "\\Q": "\\mathbb{Q}",
    "\\C": "\\mathbb{C}",
}
```

Function macros receive a `macroExpander` that can be used to expand nested macros:

```js
macros: {
    "\\frown": (macroExpander) =>
        "\\raisebox{0.5ex}{\\text{/}}\\raisebox{-0.5ex}{\\text{\\}}",
}
```

### fleqn

- **Type:** `boolean`
- **Default:** `false`

When `true`, display math renders flush left with a `2em` left margin, matching `\documentclass[fleqn]` with the `amsmath` package.

### leqno

- **Type:** `boolean`
- **Default:** `false`

When `true`, `\tag{}` renders on the left side of display math, matching `\usepackage[leqno]{amsmath}`.

### maxSize

- **Type:** `number` (ems)
- **Default:** `Infinity`

Caps user-specified sizes in commands like `\rule{500em}{500em}`. Set to a finite value (e.g., `500`) for untrusted input to prevent layout-breaking sizes.

### maxExpand

- **Type:** `number`
- **Default:** `1000`

Limits macro expansion count to prevent infinite loops. `\edef` counts all expanded tokens. Set to `Infinity` for full expansion (matching LaTeX behavior, but risks hangs).

### minRuleThickness

- **Type:** `number` (ems)
- **Default:** not set

Minimum thickness for fraction lines, `\sqrt` tops, `{array}` vertical lines, `\hline`, `\hdashline`, `\underline`, `\overline`, and `\fbox`/`\boxed`/`\fcolorbox` borders. Default rule thickness is `0.04em`; set slightly above (e.g., `0.05`) to thicken all rules. Negative values are ignored.

### colorIsTextColor

- **Type:** `boolean`
- **Default:** not set

When `true`, `\color` behaves like the legacy pre-0.8.0 KaTeX / MathJax behavior where content is a function argument: `\color{blue}{hello}`. Modern KaTeX treats `\color` as a switch: `\color{blue} hello` (matching LaTeX).

### globalGroup

- **Type:** `boolean`
- **Default:** `false`

When `true`, macros defined via `\def` and `\newcommand` at the top level are added to the `macros` option object and persist across subsequent render calls. When `false` (default), each render call runs in an isolated group, matching LaTeX's behavior where `\begin{equation}` and `$$` create local groups.

## TrustContext Type

```ts
type TrustContext =
    | { command: "\\url"; url: string; protocol?: string }
    | { command: "\\href"; url: string; protocol?: string }
    | { command: "\\includegraphics"; url: string; protocol?: string }
    | { command: "\\htmlClass"; class: string }
    | { command: "\\htmlId"; id: string }
    | { command: "\\htmlStyle"; style: string }
    | { command: "\\htmlData"; attributes: Record<string, string> }
```

## StrictFunction Type

```ts
type StrictFunction = (
    errorCode:
        | "unknownSymbol"
        | "unicodeTextInMathMode"
        | "mathVsTextUnits"
        | "commentAtEnd"
        | "htmlExtension"
        | "newLineInDisplayMode",
    errorMsg: string,
    token: Token,
) => boolean | "error" | "warn" | "ignore" | undefined;
```

## ParseError

```ts
class ParseError {
    name: "ParseError";
    message: string;       // formatted message with source context
    rawMessage: string;    // raw error message
    position: number;      // character position in input
    length: number;        // length of problematic token
}
```
