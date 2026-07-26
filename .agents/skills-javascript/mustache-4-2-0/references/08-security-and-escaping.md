# Security and Escaping

## Default HTML escaping

By default, `{{variable}}` output is HTML-escaped to prevent XSS. The `Mustache.escape` function escapes 8 characters:

| Character | Entity |
|---|---|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `'` | `&#39;` |
| `/` | `&#x2F;` |
| `` ` `` | `&#x60;` |
| `=` | `&#x3D;` |

This covers the standard XSS vectors plus `/`, `` ` ``, and `=` for added safety with event handlers and protocol handlers.

## Disabling escaping

For non-HTML formats (JSON, plain text, XML), override the escape function:

```js
// No escaping — safe for plain text / JSON
Mustache.escape = (text) => text;

// Per-render override
Mustache.render(template, view, {}, { escape: (text) => text });
```

## XML escaping

For XML output, use a different escape function:

```js
Mustache.escape = (text) => String(text)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&apos;');
```

## Raw output risks

`{{{variable}}}` and `{{&variable}}` skip all escaping. Never use raw output with untrusted user data in HTML contexts.

```js
// Dangerous with user input
Mustache.render('{{{user_comment}}}', { user_comment: '<script>alert(1)</script>' });
// Outputs: <script>alert(1)</script>  — XSS!

// Safe — escaped
Mustache.render('{{user_comment}}', { user_comment: '<script>alert(1)</script>' });
// Outputs: &lt;script&gt;alert(1)&lt;/script&gt;
```

## Numbers

Numeric values bypass escaping entirely — they are converted to string directly. This is safe because numbers cannot contain HTML entities.

## Higher-order sections

Lambdas receive raw template text and a render function. The render function applies normal escaping rules. The lambda's return value is inserted as-is (not escaped). Be careful:

```js
// This lambda's output is NOT escaped
htmlify: function () {
  return function (text, render) {
    return '<div>' + render(text) + '</div>';  // render() escapes, but <div> is raw
  };
}
```

The `<div>` tags are added by the lambda and are not escaped. This is by design — lambdas are trusted code.

## Context lookup and prototype pollution

Mustache.js checks `hasProperty()` which uses the `in` operator, so it does walk the prototype chain for property lookups. However, it does not use `Object.prototype` methods directly on view data.

For untrusted view data, be aware that inherited properties could be resolved. Use a plain object or `Object.create(null)` as the view to avoid prototype properties:

```js
const safeView = Object.create(null);
safeView.name = 'Alice';
Mustache.render('{{name}} {{constructor}}', safeView);
// "Alice " — constructor is not found
```

## Best practices

1. **Keep default escaping for HTML** — only disable when templating non-HTML formats
2. **Never use `{{{ }}}` with user input** — raw output is for trusted content only
3. **Use `Object.create(null)` for untrusted data** — avoids prototype property leaks
4. **Per-render config over global override** — use `{ escape: fn }` in `render()` instead of mutating `Mustache.escape`
5. **Lambdas are trusted** — higher-order section functions are code, not data. Do not construct them from user input
