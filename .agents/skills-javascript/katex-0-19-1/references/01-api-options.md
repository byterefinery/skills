# API and Options Reference

Full option semantics for `katex.render(tex, element, options?)` and `katex.renderToString(tex, options?)`, from `docs/options.md`, `docs/api.md`, and `types/katex.d.ts` (v0.19.1).

## displayMode

`boolean`, default `false`. If `true`, math is rendered in display mode:

- Display mode starts in `\displaystyle` (`\int`, `\sum` are large); inline mode starts in `\textstyle` (sub/superscripts usually don't stack on operators). Switch manually with `\displaystyle` / `\textstyle`.
- Display mode centers math on its own line and disables automatic line breaking (customize via custom CSS). In inline mode, KaTeX allows line breaks after outermost relations (`=`, `<`) or binary operators (`+`, `\times`), same as TeX.

## output

`string`. Markup language of the output:

- `"html"` — HTML only
- `"mathml"` — MathML only
- `"htmlAndMathml"` — HTML for visual rendering plus MathML for accessibility. The default.

## leqno / fleqn

Both `boolean`, default `false`. `leqno`: display math renders `\tag`s on the left, like `\usepackage[leqno]{amsmath}`. `fleqn`: display math renders flush left with a 2em left margin, like `\documentclass[fleqn]` with amsmath.

## throwOnError / errorColor

`throwOnError`: `boolean`, default `true`. If `true`, a `ParseError` is thrown on unsupported commands or invalid LaTeX. If `false`, unsupported commands render as text and invalid LaTeX renders as its source code with hover text giving the error, in `errorColor`.

`errorColor`: `string`, `"#XXX"` or `"#XXXXXX"`, default `"#cc0000"`.

## macros

`object`. A collection of custom macros. Each key is either a backslash-prefixed command name (`"\\foo"` defines `\foo`) or a single character (defining the equivalent of a TeX active character). Each value is one of:

- A **string** with the LaTeX expansion (recursively expanded when used). Can invoke required arguments via `#1`, `#2`, etc.
- A **function** accepting an instance of `MacroExpander` (internal API, subject to non-backwards compatible changes — see `src/defineMacro.js`) and returning the expansion string.
- An **expansion object** matching the internal `MacroExpansion` specification — what results from global `\def` or `\let`. Example simulating `\let\realint=\int`:

```js
{"\\realint": {tokens: [{text: "\\int", noexpand: true}], numArgs: 0}}
```

**This object is modified** if the LaTeX code defines its own macros via `\gdef` or `\global\let` (or via `\def`/`\newcommand`/`\let` when using `globalGroup`). Pass the same `macros` object into consecutive calls to share state (in particular, user macro definitions) across calls.

### Persistent macros (from `docs/api.md`)

`\gdef` creates macros that persist between KaTeX elements — but only if you create **one shared `macros` object** and pass it into every call (do not create a fresh object per call):

```js
const macros = {};
for (let element of mathElements) {
    katex.render(element.textContent, element, {
        throwOnError: false,
        macros
    });
}
```

**Security of persistent macros:** they can change KaTeX's behavior (e.g. redefining standard commands). Use such a setup only for multiple elements of common trust — e.g. one `macros` object per user's message — not across messages posted by multiple users.

## minRuleThickness

`number`. Minimum thickness in ems for fraction lines, `\sqrt` top lines, `{array}` vertical lines, `\hline`, `\hdashline`, `\underline`, `\overline`, and the borders of `\fbox`, `\boxed`, `\fcolorbox`. The usual thickness is `0.04`, so use a value slightly above it (e.g. `0.05` or `0.06`) for the option to have any effect. Negative values are ignored.

## colorIsTextColor

`boolean`. Early KaTeX (<0.8.0) and MathJax expected `\color{blue}{hello}` (content as function argument); current KaTeX treats `\color` as a switch, `\color{blue} hello` (matching LaTeX). Set `true` for the old behavior.

## maxSize

`number`. All user-specified sizes (e.g. in `\rule{500em}{500em}`) are capped to `maxSize` ems. Default `Infinity` — users can make elements and spaces arbitrarily large.

## maxExpand

`number`. Limits macro expansions to prevent infinite macro loops. `\edef` expansion counts all expanded tokens. `Infinity` tries to fully expand, as in LaTeX. Default `1000`.

## strict

`boolean` or `string` or `function`, default `"warn"`. Controls strict LaTeX faithfulness and symbol handling:

- `false` / `"ignore"` — allow arbitrary Unicode symbols (may lay out poorly) and convenient features not actually supported by (Xe)LaTeX (similar to MathJax).
- `true` / `"error"` — throw for any such transgressions, enforcing symbols with known metrics and input that should render faithfully in LaTeX.
- `"warn"` (default) — warn via `console.warn`.
- Custom function `handler(errorCode, errorMsg, token)` to customize behavior per transgression; may return `"ignore"`, `"error"`, or `"warn"` to use a built-in behavior.

v0.19.0 TypeScript note: `StrictFunction`'s return type no longer includes `undefined` (a function that can fall through without returning no longer typechecks), and its `token` parameter is now optional (`token?: Token`) — check it before using, e.g. `token?.loc`.

Error codes that can throw (first category):

| `errorCode` | Meaning |
|---|---|
| `unknownSymbol` | Unknown Unicode symbol; likely missing metrics and incorrect layouts (especially vertical heights) |
| `unicodeTextInMathMode` | Unicode text characters used in math mode |
| `mathVsTextUnits` | Mismatch of math vs. text commands and units/mode |
| `commentAtEnd` | `%` comment without terminating newline — LaTeX would comment out the end of math mode (e.g. `$`) |
| `htmlExtension` | Use of `\html`-prefixed HTML manipulation commands |
| `mathVsSout` | `\sout` used in math mode (LaTeX's works only in text mode) |
| `mathVsTextAccents` | Text-mode accent command (`\'`, `\"`, `\c`, `\textcircled`) used in math mode; KaTeX renders the argument in text mode anyway |
| `textEnv` | A row of an `{array}` environment has more `&`-separated cells than the column argument declares |
| `symbolNotInFont` | No character metrics for a symbol in the given style and mode (new in v0.19.0) |

Second category — never throws, but strictness affects behavior:

| `errorCode` | Meaning |
|---|---|
| `newLineInDisplayMode` | `\\` or `\newline` in display mode outside an array/tabular environment. In strict mode no line break results, as in LaTeX. |

v0.19.0 behavior change for missing metrics: previously always a plain `console.warn` (`No character metrics for '…' in style '…' and mode '…'`). Now reported through `strict` as `symbolNotInFont` — the default `"warn"` still warns but with the message `LaTeX-incompatible input and strict mode is set to 'warn': No character metrics for '…' in style '…' and mode '…' [symbolNotInFont]`; `"error"`/`true` throws a `ParseError`; `"ignore"`/`false` prints nothing. To keep the old behavior for this case only while staying strict:

```js
katex.render(tex, element, {
    strict: (errorCode) =>
        errorCode === "symbolNotInFont" ? "warn" : "error",
});
```

v0.19.0: a `strict` function returning `undefined` or `null` used to be treated like `"ignore"`; it is now treated like `"warn"`. Return `false` or `"ignore"` explicitly to suppress:

```js
// Before (v0.19 breaks this)
strict: (errorCode) => {
    if (errorCode === "unicodeTextInMathMode") {
        return "error";
    }
}

// After
strict: (errorCode) => {
    if (errorCode === "unicodeTextInMathMode") {
        return "error";
    }
    return "ignore";
}
```

## trust

`boolean` or `function`, default `false`. If `false`, commands like `\includegraphics` that could enable adverse behavior are rendered in `errorColor`. If `true`, all are allowed. A custom function `handler(context)` customizes behavior by context.

Context shapes (from `types/katex.d.ts`):

```ts
{ command: "\\url", url: string, protocol?: string }
{ command: "\\href", url: string, protocol?: string }
{ command: "\\includegraphics", url: string, protocol?: string }
{ command: "\\htmlClass", class: string }
{ command: "\\htmlId", id: string }
{ command: "\\htmlStyle", style: string }
{ command: "\\htmlData", attributes: Record<string, string> }
```

`protocol` is a lowercased string like `"http"` or `"https"` appearing before a colon, or `"_relative"` for relative URLs.

Sample settings from the docs:

```js
trust: (context) => context.command !== '\\includegraphics'                    // forbid one command
trust: (context) => context.command === '\\url'                               // allow one command
trust: (context) => ['\\url', '\\href'].includes(context.command)             // allow a set of commands
trust: (context) => context.protocol === 'http'                               // allow one protocol
trust: (context) => ['http', 'https', '_relative'].includes(context.protocol) // allow a set of protocols
trust: (context) => context.protocol !== 'file'                               // forbid one protocol
trust: (context) => ['\\url', '\\href'].includes(context.command) &&
    ['http', 'https', '_relative'].includes(context.protocol)                // commands + protocols
```

## globalGroup

`boolean`, default `false`. Run KaTeX code in the global group: macros defined at top level by `\def` and `\newcommand` are added to the `macros` argument and can be used in subsequent render calls. In LaTeX, constructs such as `\begin{equation}` and `$$` create a local group preventing definitions other than `\gdef` from becoming visible outside those blocks — hence KaTeX's default.

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
