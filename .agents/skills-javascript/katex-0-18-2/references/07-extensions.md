# 07 — Extensions

## copy-tex

Intercepts clipboard copy events on `.katex` elements and replaces the copied content with the original LaTeX source.

### Loading

```html
<script src="https://cdn.jsdelivr.net/npm/katex@0.18.2/dist/contrib/copy-tex.min.js"></script>
```

```js
import "katex/contrib/copy-tex";
```

### Behavior

- When the user selects and copies a rendered formula, the clipboard receives the LaTeX source
- Partial selections within a formula are expanded to the entire formula
- Works with `htmlAndMathml` and `html` output modes
- Requires MathML in the output for detection (checks for `.katex-mathml` elements)

### Gotchas

- Installs a global `document.addEventListener("copy", ...)` handler
- Do not combine with other clipboard handlers on the same elements
- If you need custom clipboard behavior, apply copy-tex after your handler or use `stopPropagation`

## mathtex-script-type

Auto-renders `<script type="math/tex">` tags on page load.

### Loading

```html
<script src="https://cdn.jsdelivr.net/npm/katex@0.18.2/dist/contrib/mathtex-script-type.min.js"></script>
```

```js
import "katex/contrib/mathtex-script-type";
```

### Usage

```html
<!-- Inline math -->
<script type="math/tex">x^2 + y^2 = r^2</script>

<!-- Display math -->
<script type="math/tex; mode=display">
    \sum_{i=1}^n i = \frac{n(n+1)}{2}
</script>
```

### Behavior

- Scans all `<script>` elements on page load
- Matches `type="math/tex"` or `type="math/tex; mode=display"`
- Replaces each matched script with a rendered `<span>` (inline) or `<div>` (display)
- On parse errors, falls back to showing the raw TeX text

### Gotchas

- Must be loaded/executed after the DOM is ready
- Only runs once at load time — dynamically added scripts are not processed
- Script tags are removed from the DOM after processing

## render-a11y-string

Generates human-readable strings for screen readers and accessibility tools.

### Loading

```js
import renderA11yString from "katex/contrib/render-a11y-string";
```

```html
<script src="https://cdn.jsdelivr.net/npm/katex@0.18.2/dist/contrib/render-a11y-string.min.js"></script>
```

### Usage

```js
renderA11yString("\\frac{1}{2}");
// "start fraction, 1, divided by, 2, end fraction"

renderA11yString("f(x) = x^2");
// "f, left parenthesis, x, right parenthesis, equals, x, squared"

renderA11yString("\\int_0^\\infty e^{-x} dx");
// "integral, from 0, to infinity, e, to the power of negative x, d x"
```

### Options

Accepts the same `KatexOptions` as `katex.render()`:

```js
renderA11yString("\\frac{a}{b}", { displayMode: true });
```

### Limitations

- Simple expressions produce meaningful semantic descriptions
- Complex expressions produce literal token-by-token descriptions
- Not a substitute for proper MathML output — use `output: "htmlAndMathml"` for production accessibility
- Best used as a supplement, not replacement, for MathML
