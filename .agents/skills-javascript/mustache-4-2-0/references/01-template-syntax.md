# Template Syntax

## Variables

The basic building block. `{{name}}` looks up the key `name` in the current context and HTML-escapes the result.

### Lookup rules

- Search current context first, then walk up parent contexts
- If not found, renders as empty string (never `"undefined"`)
- If the value is a function, it is called with `this` as the current view; return value is used
- Numbers render directly without escaping
- `null` and `undefined` render as empty string

```js
Mustache.render('{{name}}', { name: 'Alice' });
// "Alice"

Mustache.render('{{missing}}', {});
// "" (empty string)

Mustache.render('{{count}}', { count: 42 });
// "42"
```

### Dot notation

Access nested properties with `.`:

```js
Mustache.render('{{user.name}} {{user.address.city}}', {
  user: {
    name: 'Alice',
    address: { city: 'Portland' }
  }
});
// "Alice Portland"
```

Dot notation traverses the chain depth-first within the current context. If any intermediate value is `null`/`undefined`, the whole expression renders empty.

### Current item (`{{.}}`)

Inside array iteration sections, `{{.}}` refers to the current item:

```js
Mustache.render('{{#tags}}{{.}} {{/tags}}', {
  tags: ['js', 'css', 'html']
});
// "js css html "
```

This is the standard way to iterate arrays of primitives.

## Raw (unescaped) output

By default all `{{ }}` output is HTML-escaped. To render raw:

```
{{{name}}}    — triple mustache (recommended)
{{&name}}     — ampersand (legacy Mustache syntax)
```

Both are equivalent. Escaped characters by default:

| Char | Entity |
|---|---|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `'` | `&#39;` |
| `/` | `&#x2F;` |
| `` ` `` | `&#x60;` |
| `=` | `&#x3D;` |

```js
const view = { html: '<b>Bold</b>' };
Mustache.render('{{html}}', view);
// "&lt;b&gt;Bold&lt;/b&gt;"

Mustache.render('{{{html}}}', view);
// "<b>Bold</b>"

Mustache.render('{{&html}}', view);
// "<b>Bold</b>"
```

## Comments

Comments begin with `!` and are completely stripped from output:

```
{{! This is a comment }}
```

Comments may span multiple lines:

```
{{!
  This is a
  multi-line comment
}}
```

Everything between `{{!` and `}}` is discarded, including newlines.

## Set Delimiter

Change tag delimiters inline within a template:

```
{{ default }}
{{=<% %>=}}
<% erb_style %>
<%={{ }}=%>
{{ default_again }}
```

Rules:
- Delimiters cannot contain whitespace or `=`
- The change is scoped to the template region after the set-delimiter tag
- Use the original delimiters to set new ones: `{{=<% %>=}}` not `<%={{ }}=%>` (the latter uses the new delimiters)
- Custom delimiters are respected in partials if passed via config

## Whitespace

Mustache.js performs *standalone line* stripping: if a tag is the only content on a line (surrounded only by whitespace), the entire line (including its newline) is stripped from output. This applies to sections, inverted sections, partials, and set-delimiter tags.

Regular `{{ }}` variable tags do not trigger standalone stripping.
