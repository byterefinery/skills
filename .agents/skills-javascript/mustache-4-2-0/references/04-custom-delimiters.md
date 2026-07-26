# Custom Delimiters

Mustache supports changing tag delimiters from the default `{{ }}` to any other pair of strings.

## Inline in templates

Use the set-delimiter tag within a template:

```
{{ default_var }}
{{=<% %>=}}
<% erb_style_var %>
<%={{ }}=%>
{{ back_to_default }}
```

The syntax is `{{=OPENING CLOSING=}}` where `OPENING` and `CLOSING` are the new delimiter strings separated by whitespace.

### Rules

- Delimiters cannot contain whitespace
- Delimiters cannot contain `=`
- The set-delimiter tag itself uses the *current* delimiters
- Changes are scoped to the template region after the tag
- Multiple set-delimiter tags can appear in one template

### Example

```js
Mustache.render(
  '{{ foo }}{{=<% %>=}}<% bar %><%={{ }}=%>{{ baz }}',
  { foo: '1', bar: '2', baz: '3' }
);
// "123"
```

## Programmatic

Pass custom delimiters as the 4th argument to `render()`:

```js
// As array (shorthand)
Mustache.render(template, view, {}, ['<%', '%>']);

// As config object
Mustache.render(template, view, {}, { tags: ['<%', '%>'] });

// Combined with custom escape
Mustache.render(template, view, {}, {
  tags: ['<%', '%>'],
  escape: (text) => text
});
```

This does **not** mutate `Mustache.tags`. The custom delimiters are scoped to the render call.

## Global override

Set `Mustache.tags` directly to change the default for all subsequent calls:

```js
Mustache.tags = ['<%', '%>'];
// All future render() calls use <% %> by default
```

Use with caution in shared environments — this affects all code using the global Mustache instance.

## Cache implications

The template cache key includes the delimiter pair. The same template string parsed with different delimiters produces separate cache entries:

```js
Mustache.parse('{{foo}}');           // cached as "{{foo}}:{{:}}"
Mustache.parse('<%foo%>', ['<%', '%>']); // cached as "<%foo%>:<%:%>"
```

This means changing delimiters does not invalidate the cache for the default-delimiter version.

## Use cases

- **TeX / LaTeX**: where `{{ }}` appears naturally in math notation
- **ERB compatibility**: `<% %>` matches Ruby ERB syntax
- **Avoiding conflicts**: when template content contains literal `{{ }}`
- **Config files**: use delimiters that don't appear in the target format
