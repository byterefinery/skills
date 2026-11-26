# 04 — Error Handling

## ParseError

When `throwOnError: true` (the default), invalid LaTeX throws a `katex.ParseError`:

```js
try {
    katex.render("\\invalid{cmd}", element);
} catch (e) {
    if (e instanceof katex.ParseError) {
        console.error(e.message);     // "Undefined control sequence \\invalid at character 0: ..."
        console.error(e.rawMessage);  // "Undefined control sequence \\invalid"
        console.error(e.position);    // 0 — character position in input
        console.error(e.length);      // length of the problematic token
    }
}
```

### Properties

| Property | Type | Description |
|---|---|---|
| `name` | `"ParseError"` | Always `"ParseError"` |
| `message` | `string` | Formatted message including source context |
| `rawMessage` | `string` | Raw error message without source context |
| `position` | `number` | Character offset where the error occurred |
| `length` | `number` | Length of the token causing the error |

The `message` property contains LaTeX source text and must be escaped before inserting into HTML.

## throwOnError: false

When `throwOnError: false`, invalid input renders as text in `errorColor` (default `#cc0000`) with the error message shown on hover. This is the recommended setting for production apps with user-supplied input.

```js
katex.renderToString("\\invalid", { throwOnError: false });
// Renders the source text in red with error on hover
```

### What Gets Rendered as Error Text

- Undefined control sequences (e.g., `\foo`)
- Mismatched delimiters
- Invalid arguments
- Unsupported LaTeX constructs
- Unicode characters in math mode (when `strict` is enabled)

## Custom Error Rendering

Combine `throwOnError: false` with `errorColor` to customize error appearance:

```js
katex.renderToString("\\invalid", {
    throwOnError: false,
    errorColor: "#ff6600",
});
```

## Auto-Render Error Callback

The auto-render extension calls `errorCallback` for each failed expression:

```js
renderMathInElement(document.body, {
    errorCallback: (msg, err) => {
        // msg: "KaTeX auto-render: Failed to parse `...` with "
        // err: katex.ParseError
        console.warn(msg, err.rawMessage);
        // The failed expression is left as raw text in the DOM
    },
});
```

Failed expressions are replaced with their raw source text (including delimiters), so they remain visible but unrendered.

## Graceful Degradation Strategy

For untrusted input, use this pattern:

```js
function safeRender(tex, element) {
    try {
        katex.render(tex, element, {
            throwOnError: true,
            trust: false,
            strict: "warn",
            maxSize: 500,
            maxExpand: 500,
        });
    } catch (e) {
        if (e instanceof katex.ParseError) {
            // Fallback: render as plain text
            element.textContent = tex;
            element.style.color = "#cc0000";
        } else {
            throw e;  // Re-throw non-parse errors
        }
    }
}
```

## Common Error Messages

| Error | Cause | Fix |
|---|---|---|
| `Undefined control sequence \foo` | Unknown command | Check spelling, load required extension |
| `Expected }` | Missing closing brace | Balance `{` and `}` |
| `LaTeX Error: \\begin{align} unmatched` | Missing `\end{align}` | Add matching end |
| `Expected to find '}'` | Mismatched grouping | Check brace nesting |
| `Lexing error: extra `}`` | Extra closing brace | Remove unmatched `}` |
