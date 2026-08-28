# x-component Directive Reference

## Directives

| Directive | Source | Description |
|---|---|---|
| `x-component="expression"` | on-page `<template id="...">` | Resolves the expression to a template id and renders that template's content |
| `x-component.url="expression"` | URL | Resolves the expression to an `http(s)` URL on the current origin, fetches and renders it |
| `x-component.url.external="expression"` | URL | As above, but cross-origin `http(s)` URLs are allowed |

`url` switches the source to URL mode; `external` only matters in URL mode.

## Expression normalization

The expression is evaluated by Alpine, then normalized:

- `string` — trimmed and used as-is
- `number` / `boolean` / any other value — `String(value)`, then trimmed
- `null` / `undefined` / empty string — treated as an empty source

An empty source unmounts and clears any mounted component. That makes `x-component="flag ? 'tpl' : null"` a clean conditional-rendering pattern.

## On-page templates

The template id is looked up with `document.getElementById`, so ids are page-global and case-sensitive. The `<template>` element stays in the document; its `innerHTML` is parsed into a fragment once, cached, and cloned on each render.

```html
<template id="person-card">
  <article>
    <h2 x-text="item.name"></h2>
  </article>
</template>
```

A missing id produces a console warning (`[alpinejs-component] Missing template: "..."`), renders nothing, and emits `x-component:error`.

## Remote URLs

URLs are resolved against the page location and validated:

- Protocol must be `http:` or `https:` — anything else throws
- Must be same-origin unless `.external` is present
- The normalized absolute URL is the cache key

Non-2xx responses throw `Request failed (<status>) for <url>`. Both cases surface as `x-component:error`.

## Dynamic values

The expression re-evaluates on every reactive dependency change, and the component remounts on each change (old tree destroyed first). Overlapping async renders are guarded by a render token — a response that lands after a newer render started is discarded.

```html
<div x-data="{ remoteView: '/public/a.html' }">
  <div x-component.url="remoteView"></div>
  <button x-on:click="remoteView = '/public/b.html'">Swap</button>
</div>
```

## The host element

When a component mounts, the host element's existing children (e.g., a loading placeholder) are destroyed and replaced with the rendered component content. On every source change or unmount, the previously mounted tree is torn down via `Alpine.destroyTree`, so interval/timer side effects inside a component are cleaned up.

## Inside `x-for`

Wrap the host element in a keyed `<template x-for>`, and give each iteration its own scope when the template references per-item data:

```html
<ul>
  <template x-for="person in people" :key="person.name">
    <li>
      <div x-data="{ item: person }" x-component="'person-card'"></div>
    </li>
  </template>
</ul>
```
