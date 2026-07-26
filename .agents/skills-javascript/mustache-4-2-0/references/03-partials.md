# Partials

Partials enable template composition. They are resolved at render time, not compile time.

## Syntax

```
{{> partial_name}}
```

## Registration

Pass an object keyed by partial name, valued by template string, as the third argument to `render()`:

```js
Mustache.render(template, view, {
  header: '<header>{{title}}</header>',
  footer: '<footer>&copy; {{year}}</footer>'
});
```

## Context inheritance

Partials inherit the calling context. Variables available in the parent template are available in the partial:

```js
// base.mustache
<h2>Names</h2>
{{#names}}
  {{> user}}
{{/names}}

// user.mustache
<strong>{{name}}</strong>
```

```js
Mustache.render(base, {
  names: [{ name: 'Alice' }, { name: 'Bob' }]
}, { user: userTemplate });
// "<h2>Names</h2>\n  <strong>Alice</strong>\n  <strong>Bob</strong>"
```

## Indentation

When a partial is the **first tag on its line**, its output is auto-indented to match the partial tag's indentation. This preserves formatting when partials are nested inside indented blocks:

```
{{#items}}
  {{> item}}
{{/items}}
```

If `item.mustache` is:

```
<li>{{name}}</li>
```

The output preserves the indentation:

```
  <li>Alice</li>
  <li>Bob</li>
```

Only spaces and tabs are used for indentation (other whitespace characters are stripped from the indent prefix).

If the partial is not the first tag on its line, no indentation is applied.

## Recursive partials

Since partials are resolved at render time, recursive partials are possible:

```js
const folder = '<li>{{name}}{{#children}}{{> folder}}{{/children}}</li>';

Mustache.render('{{> folder}}', {
  name: 'root',
  children: [{ name: 'child', children: [] }]
}, { folder });
// "<li>root<li>child</li></li>"
```

Avoid infinite loops — there is no recursion depth limit.

## Dynamic partials

The partials argument can be a function instead of an object. The function receives the partial name and returns the template string:

```js
Mustache.render(template, view, function (partialName) {
  return loadPartial(partialName);  // your loader
});
```

This enables lazy loading of partials.

## Partials with custom delimiters

When using custom delimiters, pass them via the config (4th argument). Partials are parsed with the same delimiters:

```js
Mustache.render(
  '<%> header %>',
  {},
  { header: '<% title %>' },
  { tags: ['<%', '%>'] }
);
```

## Partials in sections

Partials inside sections inherit the section's context:

```js
// Template
{{#users}}
  {{> user_card}}
{{/users}}

// Partial
<div>{{name}} — {{role}}</div>
```

Each iteration of the section provides a different context to the partial.
